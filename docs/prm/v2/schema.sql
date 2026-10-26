/* =====================================================================================================================
   PRM Save · esquema do banco (Azure SQL Database, serverless, Brazil South, tenant Save)
   Versão 2.0 · 26/10/2026 · dono: Dados & BI (Área Partners) · desenho: docs/prm/v2/03-dados.md
   ---------------------------------------------------------------------------------------------------------------------
   Esquemas
     ref      listas de referência (pipeline, etapa → 7 estados, tese, produto, tipos de SLA, retenção)
     hs       espelho SÓ LEITURA do HubSpot (a Function de sincronização é a única que grava; ninguém edita)
     prm      o que nasce no PRM: parceiro, usuário, termo, registro, conflito, extrato, demanda, nível, material
     central  tabelas trazidas da Central Partners (consulta de regime, esteira/dossiê, respostas pelo histórico,
              chamados propostos, caixa de notificações, pedidos aos agentes)
     seg      segurança e LGPD (RLS, trilha de acesso, aceite de termos de uso)
     ops      sincronização, qualidade e expurgo
   Classes de dado (coluna "PII" no 03-dados.md, seção 1.3)
     P0  sem dado pessoal nem de cliente
     P1  dado pessoal de parceiro ou do time (nome, e-mail corporativo, id do Entra)       → Dynamic Data Masking
     P2  dado de cliente (CNPJ, razão social, contato do decisor, texto livre de demanda)  → Always Encrypted (Randomized)
                                                                                            + chave HMAC para busca
     P3  PROIBIDO no PRM: CPF, RG, CNH, dado bancário, senha (regra R24). Não existe coluna; a API recusa (lib/protecao.py)
   Pré-requisitos (TI da Save, uma vez, fora deste script)
     1. Chave mestra no Key Vault (RSA 3072) e, no SSMS ou PowerShell (SqlServer module), a Column Master Key CMK_PRM e a
        Column Encryption Key CEK_PRM (o valor cifrado da CEK é gerado pela ferramenta; não se escreve à mão).
     2. Identidade gerenciada da Function App com: db_datareader/db_datawriter nos esquemas hs, prm, central, ops;
        "unwrapKey/verify" no Key Vault (para decifrar P2). O painel interno (perfil Save) usa outro usuário, sem acesso à CMK:
        ele vê P2 só cifrado (busca pela chave HMAC, exibe a máscara).
     3. Segredo CENTRAL_SAL no Key Vault (o MESMO da Central): HMAC-SHA256 da raiz e do CNPJ, 32 hex (negocio_ativo.chave).
   Datas: datetime2(0) em UTC (o HubSpot devolve UTC); a tela converte para America/Sao_Paulo.
   Dinheiro: decimal(18,2). Percentual: decimal(9,6) como fração (0,30 = 30%), igual ao _pct() do hubspot_fonte.py.
   ===================================================================================================================== */

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

/* --------------------------------------------------------------------------------------------- 0. chaves (referência)
CREATE COLUMN MASTER KEY CMK_PRM WITH (KEY_STORE_PROVIDER_NAME = N'AZURE_KEY_VAULT',
     KEY_PATH = N'https://<kv-prm>.vault.azure.net/keys/prm-cmk/<versao>');
CREATE COLUMN ENCRYPTION KEY CEK_PRM WITH VALUES (COLUMN_MASTER_KEY = CMK_PRM, ALGORITHM = 'RSA_OAEP',
     ENCRYPTED_VALUE = 0x...);   -- gerado pelo SSMS / New-SqlColumnEncryptionKey
-------------------------------------------------------------------------------------------------------------------- */

CREATE SCHEMA ref;
GO
CREATE SCHEMA hs;
GO
CREATE SCHEMA prm;
GO
CREATE SCHEMA central;
GO
CREATE SCHEMA seg;
GO
CREATE SCHEMA ops;
GO

/* ===================================================================================================== 1. REFERÊNCIA */

CREATE TABLE ref.estado_parceiro (               -- os 7 estados do M3 "Meus negócios" (linguagem do parceiro)
    estado_id      tinyint       NOT NULL CONSTRAINT pk_estado_parceiro PRIMARY KEY,
    rotulo         nvarchar(40)  NOT NULL CONSTRAINT uq_estado_rotulo UNIQUE,
    bola_com       varchar(10)   NOT NULL CONSTRAINT ck_estado_bola CHECK (bola_com IN ('save','parceiro','cliente','ninguem'))
);
INSERT ref.estado_parceiro VALUES (1,N'Recebido','save'),(2,N'Em diagnóstico','save'),(3,N'Precisa de algo de você','parceiro'),
       (4,N'Apresentação marcada','save'),(5,N'Contrato em andamento','cliente'),(6,N'Em execução','save'),(7,N'Encerrado','ninguem');

CREATE TABLE ref.pipeline (
    pipeline_id    varchar(40)   NOT NULL CONSTRAINT pk_pipeline PRIMARY KEY,     -- id interno do HubSpot
    nome           nvarchar(80)  NOT NULL,
    familia        varchar(20)   NOT NULL CONSTRAINT ck_pipeline_familia CHECK (familia IN ('recuperacao','passivo','planejamento','juridico','produtos','prospeccao','outro')),
    no_prm         bit           NOT NULL CONSTRAINT df_pipeline_no_prm DEFAULT 1   -- 0 = não aparece ao parceiro (ex.: Enriquecimento)
);

CREATE TABLE ref.etapa (                         -- mapa etapa → estado do parceiro (decisão da fase 0; carga em 03-dados.md §2.3)
    pipeline_id    varchar(40)   NOT NULL CONSTRAINT fk_etapa_pipeline REFERENCES ref.pipeline(pipeline_id),
    etapa_id       varchar(40)   NOT NULL,                                        -- dealstage interno
    nome           nvarchar(80)  NOT NULL,
    status_hs      varchar(8)    NOT NULL CONSTRAINT ck_etapa_status CHECK (status_hs IN ('aberto','ganho','perdido')),
    probabilidade  decimal(5,4)  NULL,
    ordem          smallint      NOT NULL,
    estado_id      tinyint       NOT NULL CONSTRAINT fk_etapa_estado REFERENCES ref.estado_parceiro(estado_id),
    vigente_desde  date          NOT NULL CONSTRAINT df_etapa_vig DEFAULT CAST(SYSUTCDATETIME() AS date),
    CONSTRAINT pk_etapa PRIMARY KEY (pipeline_id, etapa_id)
);

CREATE TABLE ref.tese (                          -- catálogo T01–T19 (vitrine: T13 e T16 fora; Funrural em conciliação)
    tese_id        char(3)       NOT NULL CONSTRAINT pk_tese PRIMARY KEY,
    nome           nvarchar(120) NOT NULL,
    valor_hubspot  nvarchar(200) NULL,                                            -- opção da multisseleção teses_tributarias_aplicadas_neste_negocio_
    na_vitrine     bit           NOT NULL CONSTRAINT df_tese_vitrine DEFAULT 1
);

CREATE TABLE ref.produto (                       -- lista fechada da propriedade Produto (D37/D57, a criar no HubSpot)
    produto_id     varchar(30)   NOT NULL CONSTRAINT pk_produto PRIMARY KEY,
    nome           nvarchar(80)  NOT NULL,
    situacao       varchar(12)   NOT NULL CONSTRAINT ck_produto_sit CHECK (situacao IN ('pronto','descoberta','fora')),
    regra_repasse  varchar(20)   NOT NULL CONSTRAINT ck_produto_regra CHECK (regra_repasse IN ('termo_recuperacao','10_liquido_save','ci_10_30','sem_repasse')),
    dono           nvarchar(60)  NULL
);

CREATE TABLE ref.sla_tipo (                      -- 23 tipos de skills/celula-daniela/references/sla.json (proposta)
    tipo_id              varchar(30)  NOT NULL CONSTRAINT pk_sla_tipo PRIMARY KEY,
    rotulo               nvarchar(120) NOT NULL,
    categoria            nvarchar(40) NOT NULL,
    area                 nvarchar(40) NOT NULL,
    primeira_resposta_du tinyint      NULL,
    solucao_du           tinyint      NULL,                                       -- NULL = depende de prazo externo
    urgente              bit          NOT NULL CONSTRAINT df_sla_urg DEFAULT 0,
    versao               varchar(20)  NOT NULL
);

CREATE TABLE ref.feriado (data date NOT NULL CONSTRAINT pk_feriado PRIMARY KEY, nome nvarchar(80) NOT NULL);  -- para dias úteis do SLA

CREATE TABLE ref.retencao (                      -- política de retenção aplicada por ops.usp_expurgar (validar com o Jurídico)
    tabela         sysname       NOT NULL CONSTRAINT pk_retencao PRIMARY KEY,
    acao           varchar(12)   NOT NULL CONSTRAINT ck_ret_acao CHECK (acao IN ('apagar','anonimizar','substituir','manter')),
    prazo_dias     int           NULL,
    contado_de     nvarchar(60)  NOT NULL,
    base           nvarchar(200) NOT NULL
);

/* ======================================================================================= 2. ESPELHO DO HUBSPOT (hs) */

CREATE TABLE hs.negocio (                        -- 1 linha por deal; MERGE diário a partir de hs.negocio_stage
    deal_id               bigint         NOT NULL CONSTRAINT pk_hs_negocio PRIMARY KEY,
    pipeline_id           varchar(40)    NOT NULL,
    etapa_id              varchar(40)    NOT NULL,
    status_hs             varchar(8)     NOT NULL CONSTRAINT ck_hs_status CHECK (status_hs IN ('aberto','ganho','perdido')),
    estado_id             tinyint        NOT NULL CONSTRAINT fk_hs_estado REFERENCES ref.estado_parceiro(estado_id),
    -- cliente (P2)
    cnpj_cif              char(14)       COLLATE Latin1_General_BIN2
                          ENCRYPTED WITH (COLUMN_ENCRYPTION_KEY = CEK_PRM, ENCRYPTION_TYPE = RANDOMIZED, ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256') NULL,
    cnpj_hmac             char(32)       NULL,     -- HMAC(sal, CNPJ 14) → busca exata
    cnpj_raiz_hmac        char(32)       NULL,     -- HMAC(sal, raiz 8)  → registro, conflito, índice da Central
    cnpj_mascara          varchar(18)    NULL,     -- 2 primeiras e 2 últimas posições (exibição sem decifrar)
    cnpj_situacao         varchar(8)     NOT NULL CONSTRAINT ck_hs_cnpj_sit CHECK (cnpj_situacao IN ('valido','vazio','invalido')),
    empresa_nome_cif      nvarchar(200)  COLLATE Latin1_General_BIN2
                          ENCRYPTED WITH (COLUMN_ENCRYPTION_KEY = CEK_PRM, ENCRYPTION_TYPE = RANDOMIZED, ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256') NULL,
    uf                    char(2)        NULL,
    cidade                nvarchar(80)   NULL,
    regime                nvarchar(40)   NULL,
    porte                 nvarchar(40)   NULL,
    faixa_faturamento     nvarchar(60)   NULL,
    cnae                  varchar(9)     NULL,
    segmento              nvarchar(200)  NULL,
    -- canal
    parceiro_bruto        nvarchar(200)  MASKED WITH (FUNCTION = 'partial(3,"***",0)') NULL,   -- nome_do_parceiro como veio (P1 quando é pessoa)
    parceiro_id           varchar(12)    NULL,     -- resolvido por prm.parceiro_alias (NULL = sem parceiro)
    master_id             varchar(12)    NULL,
    indicado_por_email    nvarchar(200)  MASKED WITH (FUNCTION = 'email()') NULL,   -- P1
    owner_id              varchar(20)    NULL,
    -- valores (crédito estimado, não honorário nem caixa)
    valor_credito         decimal(18,2)  NULL,
    honorario_pct         decimal(9,6)   NULL,     -- honorarios_contratuais (fração)
    parceiro_pct_card     decimal(9,6)   NULL,     -- honorarios_parceiro (fração) · fonte oficial do % é prm.termo (R1)
    vendedor_pct          decimal(9,6)   NULL,
    gestor_comercial_pct  decimal(9,6)   NULL,
    indicador_pct         decimal(9,6)   NULL,
    coordenador_pct       decimal(9,6)   NULL,
    teses_hs              nvarchar(1000) NULL,     -- multisseleção crua; normalizada em hs.negocio_tese
    produto_id            varchar(30)    NULL,     -- propriedade Produto (D37) quando existir
    recebido_hs           decimal(18,2)  NULL,     -- não existe no HubSpot hoje (0 de 1.696); o recebido vem de prm.recebimento
    -- datas
    criado_em             date           NULL,     -- createdate em dia de Brasília (dia_br)
    fechado_em            date           NULL,     -- closedate como escolhido no CRM
    data_efetiva          AS (CASE WHEN status_hs <> 'aberto' AND fechado_em IS NOT NULL AND (criado_em IS NULL OR fechado_em < criado_em)
                                   THEN fechado_em ELSE criado_em END) PERSISTED,   -- menor entre criação e fechamento (importações regravaram createdate)
    entrou_etapa_em       datetime2(0)   NULL,     -- hs_v2_date_entered_current_stage
    ultima_atividade_em   datetime2(0)   NULL,     -- notes_last_updated
    hs_modificado_em      datetime2(0)   NOT NULL, -- hs_lastmodifieddate: marca d'água da carga incremental
    -- execução
    ecac_liberado         bit            NULL,
    tem_parecer           bit            NOT NULL CONSTRAINT df_hs_parecer DEFAULT 0,
    tem_anexo_diagnostico bit            NOT NULL CONSTRAINT df_hs_anexo DEFAULT 0,
    id_bitrix             varchar(20)    NULL,
    importado             bit            NOT NULL CONSTRAINT df_hs_import DEFAULT 0,
    cafe                  bit            NOT NULL CONSTRAINT df_hs_cafe DEFAULT 0,   -- regra do café (mapeamento-hubspot.json → regras)
    -- controle
    hash_linha            binary(32)     NOT NULL, -- SHA-256 das colunas de negócio: MERGE só atualiza o que mudou
    sync_id               bigint         NOT NULL,
    excluido_no_hs        bit            NOT NULL CONSTRAINT df_hs_excl DEFAULT 0,  -- some do HubSpot → marca, não apaga
    carregado_em          datetime2(0)   NOT NULL CONSTRAINT df_hs_carr DEFAULT SYSUTCDATETIME()
);
CREATE INDEX ix_hs_negocio_raiz     ON hs.negocio (cnpj_raiz_hmac, status_hs) INCLUDE (parceiro_id, master_id, pipeline_id);
CREATE INDEX ix_hs_negocio_cnpj     ON hs.negocio (cnpj_hmac) WHERE cnpj_hmac IS NOT NULL;
CREATE INDEX ix_hs_negocio_parceiro ON hs.negocio (parceiro_id, status_hs) INCLUDE (estado_id, valor_credito, fechado_em, criado_em);
CREATE INDEX ix_hs_negocio_master   ON hs.negocio (master_id, status_hs) INCLUDE (valor_credito, fechado_em);
CREATE INDEX ix_hs_negocio_mod      ON hs.negocio (hs_modificado_em);

CREATE TABLE hs.negocio_stage (                  -- área de pouso da Function (truncada a cada rodada); mesmas colunas, sem restrições
    deal_id          bigint        NOT NULL,
    json_props       nvarchar(max) NOT NULL,   -- propriedades já transformadas pela Function (P2 já cifrado pelo driver com AE)
    hs_modificado_em datetime2(0)  NOT NULL,
    sync_id          bigint        NOT NULL
);

CREATE TABLE hs.negocio_etapa_hist (             -- trilha de etapas (base de "tempo na etapa" e do funil por coorte)
    deal_id        bigint        NOT NULL,
    etapa_id       varchar(40)   NOT NULL,
    status_hs      varchar(8)    NOT NULL,
    entrou_em      datetime2(0)  NOT NULL,
    saiu_em        datetime2(0)  NULL,
    origem         varchar(12)   NOT NULL CONSTRAINT ck_hist_origem CHECK (origem IN ('sync_diff','hs_historico')),
    CONSTRAINT pk_hs_etapa_hist PRIMARY KEY (deal_id, entrou_em, etapa_id)
);

CREATE TABLE hs.negocio_tese (
    deal_id  bigint  NOT NULL CONSTRAINT fk_neg_tese_neg REFERENCES hs.negocio(deal_id),
    tese_id  char(3) NOT NULL CONSTRAINT fk_neg_tese_tese REFERENCES ref.tese(tese_id),
    CONSTRAINT pk_hs_negocio_tese PRIMARY KEY (deal_id, tese_id)
);

/* ============================================================================================== 3. PRM (fonte própria) */

CREATE TABLE prm.parceiro (                      -- escritório (Master), consultor do escritório ou indicador
    parceiro_id      varchar(12)   NOT NULL CONSTRAINT pk_parceiro PRIMARY KEY,    -- 'P-0001'
    chave            nvarchar(220) NOT NULL CONSTRAINT uq_parceiro_chave UNIQUE,   -- 'M|NOME NORMALIZADO' (idempotência da carga)
    tipo             varchar(10)   NOT NULL CONSTRAINT ck_parceiro_tipo CHECK (tipo IN ('master','consultor','indicador')),
    nome_exibicao    nvarchar(200) NOT NULL,                                       -- P1 quando é pessoa física
    master_id        varchar(12)   NULL CONSTRAINT fk_parceiro_master REFERENCES prm.parceiro(parceiro_id),
    cnpj_parceiro    char(14)      NULL,                                           -- CNPJ do escritório (dado público da PJ parceira)
    data_entrada     date          NULL,                                           -- lacuna PS-11: nasce aqui
    data_entrada_origem varchar(12) NULL CONSTRAINT ck_parceiro_ent CHECK (data_entrada_origem IN ('termo','informada','1o_negocio')),
    nivel_atual      varchar(30)   NULL,                                           -- leitura-sombra até a F8
    situacao         varchar(10)   NOT NULL CONSTRAINT ck_parceiro_sit CHECK (situacao IN ('ativo','suspenso','encerrado')),
    origem_cadastro  varchar(24)   NOT NULL,
    confirmado       bit           NOT NULL CONSTRAINT df_parceiro_conf DEFAULT 0, -- Daniela confirmou tipo e vínculo
    criado_em        datetime2(0)  NOT NULL CONSTRAINT df_parceiro_criado DEFAULT SYSUTCDATETIME(),
    valido_de        datetime2(0)  GENERATED ALWAYS AS ROW START NOT NULL,
    valido_ate       datetime2(0)  GENERATED ALWAYS AS ROW END NOT NULL,
    PERIOD FOR SYSTEM_TIME (valido_de, valido_ate),
    CONSTRAINT ck_parceiro_hierarquia CHECK ((tipo = 'consultor' AND master_id IS NOT NULL) OR (tipo <> 'consultor'))
) WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = prm.parceiro_hist, HISTORY_RETENTION_PERIOD = 5 YEARS));
CREATE INDEX ix_parceiro_master ON prm.parceiro (master_id) WHERE master_id IS NOT NULL;

CREATE TABLE prm.parceiro_alias (                -- texto livre do HubSpot → parceiro (roster + aliases-parceiros.json)
    alias_norm   nvarchar(200) NOT NULL CONSTRAINT pk_parceiro_alias PRIMARY KEY, -- maiúsculas, sem acento, espaços simples
    parceiro_id  varchar(12)   NOT NULL CONSTRAINT fk_alias_parceiro REFERENCES prm.parceiro(parceiro_id),
    origem       varchar(24)   NOT NULL,
    confirmado   bit           NOT NULL CONSTRAINT df_alias_conf DEFAULT 0
);

CREATE TABLE prm.usuario_parceiro (              -- pessoa do escritório com login (Entra B2B)
    usuario_id     varchar(12)   NOT NULL CONSTRAINT pk_usuario PRIMARY KEY,      -- 'U-0001'
    parceiro_id    varchar(12)   NOT NULL CONSTRAINT fk_usuario_parceiro REFERENCES prm.parceiro(parceiro_id),
    nome           nvarchar(160) MASKED WITH (FUNCTION = 'partial(2,"***",0)') NOT NULL,   -- P1
    email          nvarchar(200) MASKED WITH (FUNCTION = 'email()') NOT NULL,              -- P1
    email_hmac     char(32)      NOT NULL CONSTRAINT uq_usuario_email UNIQUE,     -- convite sem duplicar
    papel          varchar(10)   NOT NULL CONSTRAINT ck_usuario_papel CHECK (papel IN ('titular','consultor')),
    entra_oid      uniqueidentifier NULL CONSTRAINT uq_usuario_oid UNIQUE,        -- objectId do convidado B2B (claim oid)
    ativo          bit           NOT NULL CONSTRAINT df_usuario_ativo DEFAULT 1,
    convidado_em   datetime2(0)  NULL,
    ultimo_acesso  datetime2(0)  NULL,
    criado_em      datetime2(0)  NOT NULL CONSTRAINT df_usuario_criado DEFAULT SYSUTCDATETIME(),
    desativado_em  datetime2(0)  NULL
);
CREATE INDEX ix_usuario_parceiro ON prm.usuario_parceiro (parceiro_id) WHERE ativo = 1;

CREATE TABLE prm.termo (                         -- termo de parceria: % e vigência (fonte única do %, R1/D64)
    termo_id                varchar(16)   NOT NULL CONSTRAINT pk_termo PRIMARY KEY,
    parceiro_id             varchar(12)   NOT NULL CONSTRAINT fk_termo_parceiro REFERENCES prm.parceiro(parceiro_id),
    tipo_relacao            varchar(16)   NULL CONSTRAINT ck_termo_rel CHECK (tipo_relacao IN ('indicacao','correspondente','representacao')),
    percentual_recuperacao  decimal(9,6)  NULL CONSTRAINT ck_termo_pct CHECK (percentual_recuperacao BETWEEN 0 AND 1),
    percentual_confirmado   bit           NOT NULL CONSTRAINT df_termo_conf DEFAULT 0,
    regra_produtos_2027     varchar(20)   NOT NULL CONSTRAINT df_termo_2027 DEFAULT '10_liquido_save',
    validade_registro_dias  smallint      NULL,                                    -- 90/120/180 conforme decisão R14 e o termo
    vigencia_ini            date          NULL,
    vigencia_fim            date          NULL,
    arquivo_ref             nvarchar(400) NULL,                                    -- caminho no SharePoint de Contratos (sem o PDF no banco)
    fonte                   nvarchar(80)  NOT NULL,
    valido_de  datetime2(0) GENERATED ALWAYS AS ROW START NOT NULL,
    valido_ate datetime2(0) GENERATED ALWAYS AS ROW END NOT NULL,
    PERIOD FOR SYSTEM_TIME (valido_de, valido_ate),
    CONSTRAINT ck_termo_vig CHECK (vigencia_fim IS NULL OR vigencia_fim >= vigencia_ini)
) WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = prm.termo_hist, HISTORY_RETENTION_PERIOD = 10 YEARS));
CREATE UNIQUE INDEX ux_termo_vigente ON prm.termo (parceiro_id) WHERE vigencia_fim IS NULL;

CREATE TABLE prm.registro_oportunidade (         -- M2: nasce no PRM; liga ao deal quando a Daniela cria o card
    registro_id          varchar(14)   NOT NULL CONSTRAINT pk_registro PRIMARY KEY,   -- 'R-2026-000001'
    chave_idempotencia   uniqueidentifier NOT NULL CONSTRAINT uq_registro_idem UNIQUE,  -- gerada pelo formulário: reenvio não duplica
    parceiro_id          varchar(12)   NOT NULL CONSTRAINT fk_registro_parceiro REFERENCES prm.parceiro(parceiro_id),
    master_id            varchar(12)   NULL,
    usuario_id           varchar(12)   NULL CONSTRAINT fk_registro_usuario REFERENCES prm.usuario_parceiro(usuario_id),
    canal_entrada        varchar(10)   NOT NULL CONSTRAINT ck_registro_canal CHECK (canal_entrada IN ('portal','whatsapp','email','bdr')),
    -- cliente (P2)
    cnpj_cif             char(14)      COLLATE Latin1_General_BIN2
                         ENCRYPTED WITH (COLUMN_ENCRYPTION_KEY = CEK_PRM, ENCRYPTION_TYPE = RANDOMIZED, ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256') NOT NULL,
    cnpj_hmac            char(32)      NOT NULL,
    cnpj_raiz_hmac       char(32)      NOT NULL,
    cnpj_mascara         varchar(18)   NOT NULL,
    contato_nome_cif     nvarchar(160) COLLATE Latin1_General_BIN2
                         ENCRYPTED WITH (COLUMN_ENCRYPTION_KEY = CEK_PRM, ENCRYPTION_TYPE = RANDOMIZED, ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256') NULL,
    contato_email_cif    nvarchar(200) COLLATE Latin1_General_BIN2
                         ENCRYPTED WITH (COLUMN_ENCRYPTION_KEY = CEK_PRM, ENCRYPTION_TYPE = RANDOMIZED, ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256') NULL,
    contato_tel_cif      varchar(20)   COLLATE Latin1_General_BIN2
                         ENCRYPTED WITH (COLUMN_ENCRYPTION_KEY = CEK_PRM, ENCRYPTION_TYPE = RANDOMIZED, ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256') NULL,
    contato_cargo        nvarchar(60)  NULL,
    interesse_tipo       varchar(8)    NOT NULL CONSTRAINT ck_registro_int CHECK (interesse_tipo IN ('tese','produto','nao_sei')),
    tese_id              char(3)       NULL CONSTRAINT fk_registro_tese REFERENCES ref.tese(tese_id),
    produto_id           varchar(30)   NULL CONSTRAINT fk_registro_produto REFERENCES ref.produto(produto_id),
    como_conhece         nvarchar(400) NULL,
    evidencia_ref        nvarchar(400) NULL,                                       -- caminho do anexo no armazenamento, nunca o arquivo
    -- estado e validade (R14)
    estado               varchar(12)   NOT NULL CONSTRAINT ck_registro_estado CHECK (estado IN ('recebido','aprovado','recusado','em_conflito','expirado','convertido','cancelado')),
    resultado_checagem   varchar(24)   NOT NULL CONSTRAINT ck_registro_check CHECK (resultado_checagem IN ('livre','ja_registrado_por_voce','em_analise_area_partners')),
    motivo_checagem      varchar(30)   NULL,                                       -- interno: negocio_ativo, registro_outro_parceiro, indice_ausente, teto (nunca ao parceiro)
    criado_em            datetime2(3)  NOT NULL CONSTRAINT df_registro_criado DEFAULT SYSUTCDATETIME(),  -- carimbo que desempata (R14)
    completo_em          datetime2(3)  NULL,                                       -- vale a hora do registro COMPLETO
    decidido_em          datetime2(0)  NULL,
    decidido_por         varchar(60)   NULL,                                       -- conta do time (Entra) que aprovou/recusou
    motivo               nvarchar(400) NULL,
    valido_ate           date          NULL,
    prorrogado_ate       date          NULL,
    deal_id              bigint        NULL,                                       -- negócio criado pela Daniela no HubSpot
    vinculo_deal         varchar(12)   NULL CONSTRAINT ck_registro_vinc CHECK (vinculo_deal IN ('automatico','manual','sugerido')),
    vinculado_em         datetime2(0)  NULL,
    anonimizado_em       datetime2(0)  NULL,
    CONSTRAINT ck_registro_tese_prod CHECK (interesse_tipo = 'nao_sei' OR tese_id IS NOT NULL OR produto_id IS NOT NULL),
    CONSTRAINT ck_registro_prorroga CHECK (prorrogado_ate IS NULL OR prorrogado_ate > valido_ate)
);
-- um registro vivo por parceiro e raiz; no máximo UM aprovado por raiz (nunca duas remunerações integrais)
CREATE UNIQUE INDEX ux_registro_vivo_parceiro ON prm.registro_oportunidade (cnpj_raiz_hmac, parceiro_id) WHERE estado IN ('recebido','aprovado','em_conflito');
CREATE UNIQUE INDEX ux_registro_aprovado_raiz ON prm.registro_oportunidade (cnpj_raiz_hmac) WHERE estado = 'aprovado';
CREATE UNIQUE INDEX ux_registro_deal          ON prm.registro_oportunidade (deal_id) WHERE deal_id IS NOT NULL;
CREATE INDEX ix_registro_fila     ON prm.registro_oportunidade (estado, criado_em) INCLUDE (parceiro_id, cnpj_mascara, valido_ate);
CREATE INDEX ix_registro_validade ON prm.registro_oportunidade (valido_ate) WHERE estado = 'aprovado';
CREATE INDEX ix_registro_parceiro ON prm.registro_oportunidade (parceiro_id, criado_em);

CREATE TABLE prm.registro_evento (               -- trilha imutável (ledger append-only): prova do carimbo de hora
    evento_id      bigint IDENTITY(1,1) NOT NULL,
    registro_id    varchar(14)   NOT NULL,
    quando         datetime2(3)  NOT NULL CONSTRAINT df_reg_ev_quando DEFAULT SYSUTCDATETIME(),
    quem           varchar(60)   NOT NULL,                                         -- usuario_id, conta do time ou 'sistema'
    de_estado      varchar(12)   NULL,
    para_estado    varchar(12)   NOT NULL,
    nota           nvarchar(400) NULL                                              -- sem dado de cliente (validado pela API)
) WITH (LEDGER = ON (APPEND_ONLY = ON));
CREATE CLUSTERED INDEX cx_registro_evento ON prm.registro_evento (registro_id, quando);

CREATE TABLE prm.conflito (                      -- fatos para o Luis decidir (R15, D98); o agente não atribui cliente
    conflito_id     varchar(14)   NOT NULL CONSTRAINT pk_conflito PRIMARY KEY,   -- 'C-2026-0001'
    cnpj_raiz_hmac  char(32)      NOT NULL,
    origem          varchar(12)   NOT NULL CONSTRAINT ck_conf_origem CHECK (origem IN ('registro','herdado_hs','sentinela')),
    tipo            varchar(20)   NOT NULL CONSTRAINT ck_conf_tipo CHECK (tipo IN ('ganho_x_ganho','ganho_x_aberto','aberto_x_aberto','registro_x_negocio','registro_x_registro')),
    envolvidos      varchar(30)   NOT NULL,                                      -- master_x_master, master_x_fora, parceiro_x_sem_parceiro...
    severidade      varchar(5)    NOT NULL CONSTRAINT ck_conf_sev CHECK (severidade IN ('alta','media','baixa')),
    fatos           nvarchar(max) NULL,                                          -- JSON: datas, etapas, valores (sem nome de cliente)
    aberto_em       datetime2(0)  NOT NULL CONSTRAINT df_conf_aberto DEFAULT SYSUTCDATETIME(),
    decisao         varchar(20)   NULL CONSTRAINT ck_conf_dec CHECK (decisao IN ('primeiro_registro','divisao_excecao','save_direto','sem_conflito')),
    parceiro_vencedor_id varchar(12) NULL,
    decidido_por    varchar(60)   NULL,
    decidido_em     datetime2(0)  NULL,
    CONSTRAINT ck_conf_decidido CHECK ((decisao IS NULL AND decidido_em IS NULL) OR (decisao IS NOT NULL AND decidido_em IS NOT NULL AND decidido_por IS NOT NULL))
);
CREATE INDEX ix_conflito_aberto ON prm.conflito (severidade, aberto_em) WHERE decisao IS NULL;
CREATE INDEX ix_conflito_raiz   ON prm.conflito (cnpj_raiz_hmac);

CREATE TABLE prm.conflito_parte (
    conflito_id  varchar(14)  NOT NULL CONSTRAINT fk_cparte_conf REFERENCES prm.conflito(conflito_id),
    parte_tipo   varchar(8)   NOT NULL CONSTRAINT ck_cparte_tipo CHECK (parte_tipo IN ('registro','deal')),
    parte_ref    varchar(20)  NOT NULL,                                           -- registro_id ou deal_id
    parceiro_id  varchar(12)  NULL,
    CONSTRAINT pk_conflito_parte PRIMARY KEY (conflito_id, parte_tipo, parte_ref)
);

CREATE TABLE prm.recebimento (                   -- LACUNA: honorário recebido por negócio (fonte: Financeiro, P5/D18)
    recebimento_id  bigint IDENTITY(1,1) NOT NULL CONSTRAINT pk_recebimento PRIMARY KEY,
    deal_id         bigint        NOT NULL,
    competencia     char(7)       NOT NULL,                                       -- 'AAAA-MM'
    tipo            varchar(16)   NOT NULL CONSTRAINT ck_receb_tipo CHECK (tipo IN ('honorario','compensacao_oficio','estorno')),
    valor           decimal(18,2) NOT NULL,
    recebido_em     date          NOT NULL,
    documento_ref   nvarchar(120) NULL,                                           -- nº da NF de serviço da Save / título
    lote_fonte      varchar(40)   NOT NULL,                                       -- arquivo do Financeiro que trouxe a linha
    chave_fonte     varchar(80)   NOT NULL CONSTRAINT uq_receb_fonte UNIQUE,      -- idempotência da carga do Financeiro
    carregado_em    datetime2(0)  NOT NULL CONSTRAINT df_receb_carr DEFAULT SYSUTCDATETIME()
);
CREATE INDEX ix_recebimento_deal ON prm.recebimento (deal_id, competencia);

CREATE TABLE prm.extrato_lote (                  -- lote mensal por parceiro (corte no fim do mês; pagamento até dia 20 de M+1, proposta R11)
    lote_id        varchar(16)   NOT NULL CONSTRAINT pk_extrato_lote PRIMARY KEY, -- 'L-2026-11-P0001'
    parceiro_id    varchar(12)   NOT NULL CONSTRAINT fk_lote_parceiro REFERENCES prm.parceiro(parceiro_id),
    competencia    char(7)       NOT NULL,
    estado         varchar(12)   NOT NULL CONSTRAINT ck_lote_estado CHECK (estado IN ('aberto','conferido','liberado','pago','contestado')),
    checklist      nvarchar(max) NULL,                                           -- JSON: termo vigente, CNPJ ativo, NF, retenções, sem bloqueio, conflito resolvido
    nf_numero      varchar(30)   NULL,
    liberado_por   varchar(60)   NULL,
    liberado_em    datetime2(0)  NULL,
    CONSTRAINT uq_lote UNIQUE (parceiro_id, competencia)
);

CREATE TABLE prm.extrato_linha (                 -- M4: previsto → recebido pela Save → liberado → pago (ou em conferência)
    linha_id         varchar(32)   NOT NULL CONSTRAINT pk_extrato_linha PRIMARY KEY,   -- 'X-<deal>-<família>-<competência>'
    deal_id          bigint        NOT NULL,
    parceiro_id      varchar(12)   NOT NULL CONSTRAINT fk_linha_parceiro REFERENCES prm.parceiro(parceiro_id),
    lote_id          varchar(16)   NULL CONSTRAINT fk_linha_lote REFERENCES prm.extrato_lote(lote_id),
    familia          varchar(20)   NOT NULL CONSTRAINT ck_linha_fam CHECK (familia IN ('recuperacao','produtos_2027','credito_internacional')),
    competencia      char(7)       NULL,
    estado           varchar(16)   NOT NULL CONSTRAINT ck_linha_estado CHECK (estado IN ('previsto','em_conferencia','recebido_save','liberado','pago','cancelado')),
    motivo           nvarchar(400) NULL,                                         -- códigos C/O/I da conferência (sem valor ao parceiro quando em conferência)
    base_contratada  decimal(18,2) NULL,                                         -- crédito × % honorário (contratado ≠ devido)
    base_recebida    decimal(18,2) NULL,                                         -- soma de prm.recebimento (R5, R8)
    percentual       decimal(9,6)  NULL,
    percentual_origem varchar(6)   NULL CONSTRAINT ck_linha_porig CHECK (percentual_origem IN ('termo','card')),
    valor_previsto   decimal(18,2) NULL,
    valor_bruto      decimal(18,2) NULL,                                         -- só com base_recebida
    retencoes        decimal(18,2) NULL,                                         -- IRRF, CSRF, ISS (detalhe em extrato_retencao)
    valor_liquido    decimal(18,2) NULL,                                         -- bruto − retenções (gravado pela Function; ledger não usa coluna calculada)
    nf_numero        varchar(30)   NULL,
    pago_em          date          NULL,
    atualizado_em    datetime2(0)  NOT NULL CONSTRAINT df_linha_atual DEFAULT SYSUTCDATETIME(),
    CONSTRAINT ck_linha_pagar_so_recebido CHECK (estado NOT IN ('recebido_save','liberado','pago') OR base_recebida IS NOT NULL),   -- R5
    CONSTRAINT ck_linha_pago CHECK (estado <> 'pago' OR (pago_em IS NOT NULL AND nf_numero IS NOT NULL)),
    CONSTRAINT ck_linha_liquido CHECK (valor_liquido IS NULL OR valor_liquido = valor_bruto - ISNULL(retencoes, 0))
) WITH (LEDGER = ON);                            -- tabela-razão atualizável: histórico à prova de adulteração (contestação)
CREATE INDEX ix_linha_parceiro ON prm.extrato_linha (parceiro_id, estado) INCLUDE (valor_previsto, valor_bruto, competencia);
CREATE INDEX ix_linha_deal     ON prm.extrato_linha (deal_id);

CREATE TABLE prm.extrato_retencao (
    linha_id  varchar(32)   NOT NULL CONSTRAINT fk_ret_linha REFERENCES prm.extrato_linha(linha_id),
    tributo   varchar(6)    NOT NULL CONSTRAINT ck_ret_trib CHECK (tributo IN ('IRRF','CSRF','ISS','INSS')),
    aliquota  decimal(9,6)  NOT NULL,
    valor     decimal(18,2) NOT NULL,
    CONSTRAINT pk_extrato_retencao PRIMARY KEY (linha_id, tributo)
);

CREATE TABLE prm.contestacao (                   -- 10 dias corridos para abrir; resposta em 5 d.u.
    contestacao_id varchar(14)   NOT NULL CONSTRAINT pk_contestacao PRIMARY KEY,
    linha_id       varchar(32)   NOT NULL CONSTRAINT fk_cont_linha REFERENCES prm.extrato_linha(linha_id),
    usuario_id     varchar(12)   NOT NULL CONSTRAINT fk_cont_usuario REFERENCES prm.usuario_parceiro(usuario_id),
    aberta_em      datetime2(0)  NOT NULL CONSTRAINT df_cont_aberta DEFAULT SYSUTCDATETIME(),
    texto          nvarchar(2000) NOT NULL,
    resposta       nvarchar(2000) NULL,
    respondida_em  datetime2(0)  NULL,
    respondida_por varchar(60)   NULL,
    causa_raiz     varchar(30)   NULL,
    prazo_resposta date          NOT NULL
);

CREATE TABLE prm.demanda (                       -- M5: mesma chave do registro único (lib/registro_demandas.py, D-AAAA-NNNN)
    demanda_id       varchar(12)   NOT NULL CONSTRAINT pk_demanda PRIMARY KEY,
    chave_origem     nvarchar(200) NOT NULL CONSTRAINT uq_demanda_chave UNIQUE,   -- pessoa+conversa (WhatsApp), P-NNNN (Central), uuid (portal)
    canal            varchar(10)   NOT NULL CONSTRAINT ck_dem_canal CHECK (canal IN ('portal','whatsapp','email')),
    parceiro_id      varchar(12)   NULL,
    usuario_id       varchar(12)   NULL,
    deal_id          bigint        NULL,
    dona             varchar(10)   NOT NULL CONSTRAINT ck_dem_dona CHECK (dona IN ('daniela','jenifer','geovana','luis')),
    tipo_sla         varchar(30)   NULL CONSTRAINT fk_dem_sla REFERENCES ref.sla_tipo(tipo_id),
    titulo           nvarchar(200) NOT NULL,                                      -- sem CPF/RG/conta (lib/protecao.py antes de gravar)
    texto_cif        nvarchar(4000) COLLATE Latin1_General_BIN2
                     ENCRYPTED WITH (COLUMN_ENCRYPTION_KEY = CEK_PRM, ENCRYPTION_TYPE = RANDOMIZED, ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256') NULL,
    estado           varchar(22)   NOT NULL CONSTRAINT ck_dem_estado CHECK (estado IN ('responder','acompanhar','em_analise','aguardando_aprovacao','resolvida','concluida','encerrada','descartado')),
    via              varchar(10)   NULL CONSTRAINT ck_dem_via CHECK (via IN ('historico','chamado','direta')),
    area             nvarchar(60)  NULL,
    chamado_glpi_id  varchar(20)   NULL,
    urgente          bit           NOT NULL CONSTRAINT df_dem_urg DEFAULT 0,
    aberta_em        datetime2(0)  NOT NULL,
    primeira_resposta_em datetime2(0) NULL,
    sla_primeira_ate datetime2(0)  NULL,
    sla_solucao_ate  datetime2(0)  NULL,
    resolvida_em     datetime2(0)  NULL,
    atualizada_em    datetime2(0)  NOT NULL CONSTRAINT df_dem_atual DEFAULT SYSUTCDATETIME()
);
CREATE INDEX ix_demanda_fila     ON prm.demanda (estado, sla_solucao_ate) INCLUDE (dona, parceiro_id, urgente);
CREATE INDEX ix_demanda_parceiro ON prm.demanda (parceiro_id, aberta_em);

CREATE TABLE prm.demanda_evento (
    demanda_id  varchar(12)   NOT NULL CONSTRAINT fk_dem_ev REFERENCES prm.demanda(demanda_id),
    quando      datetime2(0)  NOT NULL,
    evento      nvarchar(200) NOT NULL,
    quem        varchar(60)   NULL,
    CONSTRAINT pk_demanda_evento PRIMARY KEY (demanda_id, quando, evento)
);

CREATE TABLE prm.nivel_apuracao (                -- M6: leitura-sombra até a F8
    parceiro_id       varchar(12)   NOT NULL CONSTRAINT fk_nivel_parceiro REFERENCES prm.parceiro(parceiro_id),
    trimestre         char(7)       NOT NULL,                                     -- '2027-T1'
    volume_ativo_12m  decimal(18,2) NULL,                                         -- líquido Save 12 m, sem café
    ganhos_12m        int           NULL,
    conversao_12m_pct decimal(5,2)  NULL,
    honorario_preenchido_pct decimal(5,2) NULL,
    nivel             varchar(30)   NULL,
    nivel_simulado    varchar(30)   NULL,
    sombra            bit           NOT NULL CONSTRAINT df_nivel_sombra DEFAULT 1,
    carta_enviada_em  datetime2(0)  NULL,
    CONSTRAINT pk_nivel_apuracao PRIMARY KEY (parceiro_id, trimestre)
);

CREATE TABLE prm.material (                      -- M7: biblioteca (só arquivo auditado entra na vitrine)
    material_id   varchar(12)   NOT NULL CONSTRAINT pk_material PRIMARY KEY,
    produto_id    varchar(30)   NULL CONSTRAINT fk_mat_produto REFERENCES ref.produto(produto_id),
    tese_id       char(3)       NULL CONSTRAINT fk_mat_tese REFERENCES ref.tese(tese_id),
    titulo        nvarchar(200) NOT NULL,
    estado        varchar(10)   NOT NULL CONSTRAINT ck_mat_estado CHECK (estado IN ('pronto','descoberta','fora')),
    arquivo_ref   nvarchar(400) NOT NULL,
    auditado_em   datetime2(0)  NULL,
    dono          nvarchar(60)  NOT NULL,
    CONSTRAINT ck_mat_vitrine CHECK (estado <> 'pronto' OR auditado_em IS NOT NULL)
);

/* ================================================================================ 4. TRAZIDAS DA CENTRAL (central) */

CREATE TABLE central.consulta_regime (           -- trilha de consultas-regime.jsonl + histórico do parceiro (últimas 30)
    consulta_id     bigint IDENTITY(1,1) NOT NULL CONSTRAINT pk_consulta PRIMARY KEY,
    quando          datetime2(0)  NOT NULL,
    usuario_id      varchar(12)   NULL,
    parceiro_id     varchar(12)   NULL,
    cnpj_hmac       char(32)      NULL,
    cnpj_raiz_hmac  char(32)      NULL,
    faixa           varchar(16)   NOT NULL CONSTRAINT ck_cons_faixa CHECK (faixa IN ('negocio_ativo','confirmado_real','provavel_real','nao_real','sem_dado','indisponivel','invalido')),
    motivo_interno  varchar(30)   NULL,                                           -- negocio_ativo, indice_ausente, teto_diario... (nunca ao parceiro)
    ano_base        smallint      NULL,
    fonte           varchar(40)   NULL,
    do_cache        bit           NOT NULL CONSTRAINT df_cons_cache DEFAULT 0
);
CREATE INDEX ix_consulta_parceiro ON central.consulta_regime (parceiro_id, quando DESC);
CREATE INDEX ix_consulta_teto     ON central.consulta_regime (usuario_id, quando) INCLUDE (motivo_interno);   -- teto diário e alerta de varredura

CREATE TABLE central.esteira_pedido (            -- central-esteira/pedidos/E-NNNN.json
    pedido_id       varchar(10)   NOT NULL CONSTRAINT pk_esteira PRIMARY KEY,     -- 'E-0001'
    parceiro_id     varchar(12)   NOT NULL,
    usuario_id      varchar(12)   NULL,
    cnpj_hmac       char(32)      NOT NULL,
    cnpj_mascara    varchar(18)   NOT NULL,
    criado_em       datetime2(0)  NOT NULL,
    status          varchar(22)   NOT NULL CONSTRAINT ck_est_status CHECK (status IN ('recebida','aguardando_aprovacao','revisao_humana','entregue','alerta')),
    nivel           varchar(8)    NULL CONSTRAINT ck_est_nivel CHECK (nivel IN ('base','agentes')),
    enriquecer      varchar(10)   NOT NULL CONSTRAINT ck_est_enr CHECK (enriquecer IN ('pendente','feito','nao','barrado')),
    consulta_faixa  varchar(16)   NULL,
    consulta_ano_base smallint    NULL,
    dossie_json     nvarchar(max) NULL,                                           -- 9 seções (perfil público da Receita; sem dado do HubSpot)
    auditoria_ok    bit           NULL,
    auditoria_alertas int         NULL,
    aprovado_por    varchar(60)   NULL,
    registro_id     varchar(14)   NULL                                            -- se o parceiro registrou a oportunidade depois do dossiê
);
CREATE INDEX ix_esteira_parceiro ON central.esteira_pedido (parceiro_id, cnpj_hmac, criado_em DESC);

CREATE TABLE central.esteira_evento (
    pedido_id   varchar(10)   NOT NULL CONSTRAINT fk_est_ev REFERENCES central.esteira_pedido(pedido_id),
    quando      datetime2(0)  NOT NULL,
    evento      varchar(30)   NOT NULL,
    origem      varchar(12)   NULL,
    auditoria_ok bit          NULL,
    por         varchar(60)   NULL,
    CONSTRAINT pk_esteira_evento PRIMARY KEY (pedido_id, quando, evento)
);

CREATE TABLE central.resposta_historico (        -- lib/historico.py avaliar: resposta antes do GLPI
    resposta_id     bigint IDENTITY(1,1) NOT NULL CONSTRAINT pk_resp_hist PRIMARY KEY,
    demanda_id      varchar(12)   NOT NULL,
    avaliado_em     datetime2(0)  NOT NULL,
    suficiente      bit           NOT NULL,
    criterio        varchar(30)   NULL CONSTRAINT ck_resp_crit CHECK (criterio IN ('mesma_pergunta_respondida','regra_da_casa','dado_do_caso','chamado_existente')),
    confianca       decimal(4,3)  NULL,
    fontes          nvarchar(max) NULL,                                           -- JSON [{fonte, ref, data, aderencia}] sem trecho de conversa
    faltou          nvarchar(max) NULL,
    rascunho_cif    nvarchar(4000) COLLATE Latin1_General_BIN2
                    ENCRYPTED WITH (COLUMN_ENCRYPTION_KEY = CEK_PRM, ENCRYPTION_TYPE = RANDOMIZED, ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256') NULL,
    auditoria_ok    bit           NULL,                                           -- auditor de promessas
    aprovada_por    varchar(60)   NULL,                                           -- Daniela (D98): nada sai sem pessoa
    enviada_em      datetime2(0)  NULL,
    medicao         varchar(14)   NULL CONSTRAINT ck_resp_med CHECK (medicao IN ('aproveitada','parcial','diferente','sem_resposta'))   -- D28
);
CREATE INDEX ix_resp_hist_demanda ON central.resposta_historico (demanda_id, avaliado_em DESC);

CREATE TABLE central.chamado_proposto (          -- registro/chamados-propostos.json → aprovação no painel → GLPI
    demanda_id      varchar(12)   NOT NULL CONSTRAINT pk_chamado PRIMARY KEY,
    area            nvarchar(60)  NOT NULL,
    grupo           nvarchar(80)  NULL,
    titulo          nvarchar(200) NOT NULL,
    descricao_cif   nvarchar(4000) COLLATE Latin1_General_BIN2
                    ENCRYPTED WITH (COLUMN_ENCRYPTION_KEY = CEK_PRM, ENCRYPTION_TYPE = RANDOMIZED, ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256') NULL,
    urgencia        varchar(8)    NULL,
    status          varchar(14)   NOT NULL CONSTRAINT ck_ch_status CHECK (status IN ('proposto','publicado','aprovado','recusado','aberto_glpi','abrir_manual')),
    proposto_em     datetime2(0)  NOT NULL,
    decidido_por    varchar(60)   NULL,
    decidido_em     datetime2(0)  NULL,
    motivo_recusa   nvarchar(400) NULL,
    glpi_id         varchar(20)   NULL
);

CREATE TABLE central.caixa_mensagem (            -- lib/caixa.py: relatórios e notificações no painel
    mensagem_id     varchar(40)   NOT NULL CONSTRAINT pk_caixa PRIMARY KEY,       -- id estável (idempotente)
    para            varchar(10)   NOT NULL CONSTRAINT ck_caixa_para CHECK (para IN ('luis','daniela','jenifer','geovana','time','parceiro')),
    parceiro_id     varchar(12)   NULL,                                           -- quando para = 'parceiro' (portal, Fase 2)
    tipo            varchar(10)   NOT NULL CONSTRAINT ck_caixa_tipo CHECK (tipo IN ('relatorio','alerta','pedido')),
    prioridade      varchar(6)    NOT NULL CONSTRAINT df_caixa_prio DEFAULT 'normal',
    assunto         nvarchar(200) NOT NULL,
    resumo          nvarchar(2000) NOT NULL,                                      -- texto puro, sem dado sensível (regra do caixa.py)
    origem          nvarchar(60)  NULL,
    anexos          nvarchar(max) NULL,                                           -- JSON [{nome, pasta_link}]: nunca conteúdo
    acoes           nvarchar(max) NULL,                                           -- JSON [{rotulo, go}]: rota interna
    criado_em       datetime2(0)  NOT NULL,
    entregue_em     datetime2(0)  NULL,
    auditoria_ok    bit           NULL,
    CONSTRAINT ck_caixa_parceiro CHECK (para <> 'parceiro' OR parceiro_id IS NOT NULL)
);
CREATE INDEX ix_caixa_para ON central.caixa_mensagem (para, criado_em DESC);

CREATE TABLE central.caixa_leitura (
    mensagem_id  varchar(40)  NOT NULL CONSTRAINT fk_cl_msg REFERENCES central.caixa_mensagem(mensagem_id),
    leitor       varchar(60)  NOT NULL,                                           -- conta conferida (portal_contas.py)
    lida_em      datetime2(0) NOT NULL,
    CONSTRAINT pk_caixa_leitura PRIMARY KEY (mensagem_id, leitor)
);

CREATE TABLE central.pedido_agente (             -- central-agentes/registro.json (P-NNNN): pedidos do time aos agentes
    pedido_id    varchar(10)   NOT NULL CONSTRAINT pk_pedido_agente PRIMARY KEY,
    pessoa       varchar(10)   NOT NULL,
    origem       varchar(10)   NOT NULL CONSTRAINT ck_pa_origem CHECK (origem IN ('email','portal')),
    portal_id    varchar(40)   NULL,
    assunto      nvarchar(200) NOT NULL,
    codigo       varchar(20)   NULL,                                              -- catálogo de pedidos
    campos       nvarchar(max) NULL,                                              -- JSON do formulário (lib/protecao.py antes)
    recebido_em  datetime2(0)  NOT NULL,
    status       varchar(22)   NOT NULL CONSTRAINT ck_pa_status CHECK (status IN ('recebido','em_analise','aguardando_aprovacao','aprovado','nao_aprovado','nova_analise','descartado')),
    versao       int           NOT NULL CONSTRAINT df_pa_versao DEFAULT 1,
    demanda_id   varchar(12)   NULL                                               -- espelho no registro único (id_origem)
);

/* ============================================================================================= 5. SEGURANÇA (seg) */

CREATE TABLE seg.acesso_log (                    -- Marco Civil art. 15 (6 meses mínimo); aqui 12 meses
    acesso_id    bigint IDENTITY(1,1) NOT NULL CONSTRAINT pk_acesso PRIMARY KEY NONCLUSTERED,
    quando       datetime2(0)  NOT NULL CONSTRAINT df_acesso_quando DEFAULT SYSUTCDATETIME(),
    usuario_id   varchar(12)   NULL,
    conta_time   varchar(60)   NULL,
    tela         varchar(40)   NOT NULL,
    acao         varchar(40)   NOT NULL,
    alvo_ref     varchar(40)   NULL,                                              -- registro_id, deal_id, linha_id (nunca CNPJ em claro)
    ip_hmac      char(32)      NULL,                                              -- IP com HMAC (prova sem guardar o IP)
    resultado    varchar(10)   NOT NULL CONSTRAINT ck_acesso_res CHECK (resultado IN ('ok','negado','erro','teto'))
);
CREATE CLUSTERED INDEX cx_acesso_log ON seg.acesso_log (quando);
CREATE INDEX ix_acesso_usuario ON seg.acesso_log (usuario_id, quando);

CREATE TABLE seg.aceite_termo_uso (
    usuario_id   varchar(12)  NOT NULL CONSTRAINT fk_aceite_usuario REFERENCES prm.usuario_parceiro(usuario_id),
    versao_termo varchar(20)  NOT NULL,
    aceito_em    datetime2(0) NOT NULL,
    CONSTRAINT pk_aceite PRIMARY KEY (usuario_id, versao_termo)
);
GO

-- Row-Level Security: a Function grava em SESSION_CONTEXT (read_only) o perfil, o parceiro e o papel do token validado.
CREATE FUNCTION seg.fn_rls_parceiro (@parceiro_id varchar(12))
RETURNS TABLE WITH SCHEMABINDING AS
RETURN
    SELECT 1 AS permitido
    WHERE CAST(SESSION_CONTEXT(N'perfil') AS varchar(10)) IN ('save', 'sync')
       OR @parceiro_id = CAST(SESSION_CONTEXT(N'parceiro_id') AS varchar(12))
       OR (CAST(SESSION_CONTEXT(N'papel') AS varchar(10)) = 'titular'
           AND EXISTS (SELECT 1 FROM prm.parceiro p
                       WHERE p.parceiro_id = @parceiro_id AND p.master_id = CAST(SESSION_CONTEXT(N'parceiro_id') AS varchar(12))));
GO
CREATE SECURITY POLICY seg.pol_parceiro
    ADD FILTER PREDICATE seg.fn_rls_parceiro(parceiro_id) ON hs.negocio,
    ADD FILTER PREDICATE seg.fn_rls_parceiro(parceiro_id) ON prm.registro_oportunidade,
    ADD BLOCK  PREDICATE seg.fn_rls_parceiro(parceiro_id) ON prm.registro_oportunidade AFTER INSERT,
    ADD FILTER PREDICATE seg.fn_rls_parceiro(parceiro_id) ON prm.extrato_linha,
    ADD FILTER PREDICATE seg.fn_rls_parceiro(parceiro_id) ON prm.extrato_lote,
    ADD FILTER PREDICATE seg.fn_rls_parceiro(parceiro_id) ON prm.demanda,
    ADD FILTER PREDICATE seg.fn_rls_parceiro(parceiro_id) ON prm.nivel_apuracao,
    ADD FILTER PREDICATE seg.fn_rls_parceiro(parceiro_id) ON central.esteira_pedido,
    ADD FILTER PREDICATE seg.fn_rls_parceiro(parceiro_id) ON central.consulta_regime
    WITH (STATE = ON);
GO

/* ================================================================================== 6. SINCRONIZAÇÃO E QUALIDADE (ops) */

CREATE TABLE ops.sync_execucao (
    sync_id          bigint IDENTITY(1,1) NOT NULL CONSTRAINT pk_sync PRIMARY KEY,
    fonte            varchar(20)   NOT NULL CONSTRAINT ck_sync_fonte CHECK (fonte IN ('hubspot','financeiro','central','registro_demandas','bitrix')),
    modo             varchar(12)   NOT NULL CONSTRAINT ck_sync_modo CHECK (modo IN ('incremental','total','reconciliacao')),
    iniciado_em      datetime2(0)  NOT NULL CONSTRAINT df_sync_ini DEFAULT SYSUTCDATETIME(),
    terminado_em     datetime2(0)  NULL,
    marca_de         datetime2(0)  NULL,           -- hs_lastmodifieddate >= (marca anterior − 15 min)
    marca_ate        datetime2(0)  NULL,
    lidos            int           NULL,
    inseridos        int           NULL,
    atualizados      int           NULL,
    sem_mudanca      int           NULL,
    marcados_excluidos int         NULL,
    resultado        varchar(10)   NOT NULL CONSTRAINT df_sync_res DEFAULT 'rodando'
                     CONSTRAINT ck_sync_res CHECK (resultado IN ('rodando','ok','parcial','falha')),
    erro             nvarchar(2000) NULL,
    executor         varchar(30)   NOT NULL        -- 'mac:partners-manha', 'gha:diario', 'func:prm-sync'
);
CREATE UNIQUE INDEX ux_sync_um_por_vez ON ops.sync_execucao (fonte) WHERE resultado = 'rodando';   -- trava: uma carga por fonte

CREATE TABLE ops.qualidade_achado (              -- regras da seção 6 do 03-dados.md, por rodada
    sync_id     bigint       NOT NULL CONSTRAINT fk_qa_sync REFERENCES ops.sync_execucao(sync_id),
    regra       varchar(10)  NOT NULL,           -- Q01..Q15
    alvo_ref    varchar(40)  NOT NULL,           -- deal_id / registro_id / parceiro_id
    severidade  varchar(8)   NOT NULL,
    detalhe     nvarchar(400) NULL,
    CONSTRAINT pk_qualidade_achado PRIMARY KEY (sync_id, regra, alvo_ref)
);
GO

/* --------------------------------------------------------------------------------------------- views das métricas */

CREATE VIEW central.vw_indice_negocio_ativo AS   -- substitui indice-negocios-ativos.json na Fase 2 (mesma regra: aberto ou ganho, qualquer idade)
    SELECT DISTINCT cnpj_raiz_hmac AS chave FROM hs.negocio
    WHERE status_hs IN ('aberto','ganho') AND cnpj_raiz_hmac IS NOT NULL AND excluido_no_hs = 0;
GO

CREATE VIEW prm.vw_ativacao AS                   -- ativo 90 d / produtivo 12 m (metricas_ps.py); Master soma o escritório
    WITH n AS (
        SELECT parceiro_id AS pid, data_efetiva, status_hs, fechado_em FROM hs.negocio WHERE parceiro_id IS NOT NULL AND cafe = 0 AND excluido_no_hs = 0
        UNION ALL
        SELECT master_id, data_efetiva, status_hs, fechado_em FROM hs.negocio WHERE master_id IS NOT NULL AND master_id <> parceiro_id AND cafe = 0 AND excluido_no_hs = 0
    ), a AS (
        SELECT pid,
               MAX(CASE WHEN data_efetiva >= DATEADD(day, -90, CAST(SYSUTCDATETIME() AS date)) THEN 1 ELSE 0 END) AS ativo_90d,
               MAX(CASE WHEN status_hs = 'ganho' AND fechado_em >= DATEADD(day, -365, CAST(SYSUTCDATETIME() AS date)) THEN 1 ELSE 0 END) AS produtivo_12m
        FROM n GROUP BY pid
    )
    SELECT p.parceiro_id, p.tipo, p.master_id, ISNULL(a.ativo_90d, 0) AS ativo_90d, ISNULL(a.produtivo_12m, 0) AS produtivo_12m,
           CASE WHEN a.ativo_90d = 1 AND a.produtivo_12m = 1 THEN 'ativo_produtivo' WHEN a.ativo_90d = 1 THEN 'ativo_rampa'
                WHEN a.produtivo_12m = 1 THEN 'dormente' ELSE 'inativo' END AS classe
    FROM prm.parceiro p LEFT JOIN a ON a.pid = p.parceiro_id WHERE p.situacao = 'ativo';
GO

CREATE VIEW prm.vw_conflito_raiz AS              -- raízes com mais de um canal (escritório) em aberto/ganho
    SELECT cnpj_raiz_hmac, COUNT(DISTINCT ISNULL(master_id, ISNULL(parceiro_id, 'sem_parceiro'))) AS canais,
           COUNT(DISTINCT master_id) AS masters, COUNT(*) AS negocios
    FROM hs.negocio WHERE status_hs IN ('aberto','ganho') AND cnpj_raiz_hmac IS NOT NULL AND excluido_no_hs = 0
    GROUP BY cnpj_raiz_hmac HAVING COUNT(DISTINCT ISNULL(master_id, ISNULL(parceiro_id, 'sem_parceiro'))) > 1;
GO

/* ------------------------------------------------------------------------------------------ retenção (procedimento) */

INSERT ref.retencao (tabela, acao, prazo_dias, contado_de, base) VALUES
 ('hs.negocio',                     'substituir', NULL, N'cada carga',                         N'espelho; o HubSpot é a fonte'),
 ('hs.negocio_etapa_hist',          'apagar',     1825, N'saída da etapa',                     N'série histórica do funil (5 anos)'),
 ('prm.registro_oportunidade',      'anonimizar',  730, N'fim da validade sem conversão',      N'LGPD art. 15/16; contato do decisor some, carimbo e raiz ficam'),
 ('prm.registro_oportunidade#conv', 'anonimizar',  365, N'conversão em negócio',               N'contato passa a viver no HubSpot'),
 ('prm.registro_evento',            'manter',     NULL, N'—',                                  N'sem dado pessoal; prova do carimbo (ledger)'),
 ('prm.extrato_linha',              'manter',     1825, N'pagamento',                          N'CTN art. 173 e CC art. 206 §5º I (5 anos) [validar Jurídico]'),
 ('prm.contestacao',                'apagar',     1825, N'resposta',                           N'idem extrato'),
 ('prm.demanda',                    'anonimizar',  730, N'resolução',                          N'texto cifrado apagado; metadados de SLA ficam'),
 ('central.consulta_regime',        'apagar',      365, N'consulta',                           N'minuta de termos de uso da consulta (12 meses)'),
 ('central.esteira_pedido',         'apagar',      365, N'criação',                            N'idem (esteira.expurgar --dias 365)'),
 ('central.resposta_historico',     'anonimizar',  365, N'avaliação',                          N'rascunho apagado; medição D28 fica'),
 ('central.caixa_mensagem',         'apagar',      180, N'criação',                            N'notificação operacional'),
 ('seg.acesso_log',                 'apagar',      365, N'acesso',                             N'Marco Civil art. 15 (mínimo 6 meses)'),
 ('prm.usuario_parceiro',           'anonimizar',  180, N'desativação',                        N'LGPD art. 16; id fica para a trilha');
GO

CREATE PROCEDURE ops.usp_expurgar @hoje date = NULL AS
BEGIN
    SET NOCOUNT ON; SET XACT_ABORT ON;
    DECLARE @d date = ISNULL(@hoje, CAST(SYSUTCDATETIME() AS date));
    BEGIN TRAN;
    UPDATE prm.registro_oportunidade
       SET contato_nome_cif = NULL, contato_email_cif = NULL, contato_tel_cif = NULL, como_conhece = NULL, evidencia_ref = NULL, anonimizado_em = SYSUTCDATETIME()
     WHERE anonimizado_em IS NULL
       AND ((estado IN ('expirado','recusado','cancelado') AND ISNULL(prorrogado_ate, valido_ate) < DATEADD(day, -730, @d))
         OR (estado = 'convertido' AND vinculado_em < DATEADD(day, -365, @d)));
    UPDATE prm.demanda SET texto_cif = NULL WHERE resolvida_em < DATEADD(day, -730, @d) AND texto_cif IS NOT NULL;
    UPDATE central.resposta_historico SET rascunho_cif = NULL WHERE avaliado_em < DATEADD(day, -365, @d) AND rascunho_cif IS NOT NULL;
    UPDATE prm.usuario_parceiro SET nome = N'(removido)', email = CONCAT(usuario_id, N'@removido.invalid'), entra_oid = NULL
     WHERE ativo = 0 AND desativado_em < DATEADD(day, -180, @d) AND nome <> N'(removido)';
    DELETE central.esteira_evento  WHERE pedido_id IN (SELECT pedido_id FROM central.esteira_pedido WHERE criado_em < DATEADD(day, -365, @d));
    DELETE central.esteira_pedido  WHERE criado_em < DATEADD(day, -365, @d);
    DELETE central.consulta_regime WHERE quando    < DATEADD(day, -365, @d);
    DELETE central.caixa_leitura   WHERE mensagem_id IN (SELECT mensagem_id FROM central.caixa_mensagem WHERE criado_em < DATEADD(day, -180, @d));
    DELETE central.caixa_mensagem  WHERE criado_em < DATEADD(day, -180, @d);
    DELETE seg.acesso_log          WHERE quando    < DATEADD(day, -365, @d);
    DELETE hs.negocio_etapa_hist   WHERE saiu_em   < DATEADD(day, -1825, @d);
    COMMIT;
END;
GO

/* ------------------------------------------------------------------------------- classificação de sensibilidade */
ADD SENSITIVITY CLASSIFICATION TO hs.negocio.cnpj_cif, hs.negocio.empresa_nome_cif, prm.registro_oportunidade.cnpj_cif
    WITH (LABEL = 'Confidential', INFORMATION_TYPE = 'Cliente (P2)', RANK = HIGH);
ADD SENSITIVITY CLASSIFICATION TO prm.registro_oportunidade.contato_nome_cif, prm.registro_oportunidade.contato_email_cif,
    prm.registro_oportunidade.contato_tel_cif, prm.demanda.texto_cif, central.resposta_historico.rascunho_cif, central.chamado_proposto.descricao_cif
    WITH (LABEL = 'Confidential - LGPD', INFORMATION_TYPE = 'Contato / texto livre (P2)', RANK = CRITICAL);
ADD SENSITIVITY CLASSIFICATION TO prm.usuario_parceiro.nome, prm.usuario_parceiro.email, hs.negocio.indicado_por_email, hs.negocio.parceiro_bruto
    WITH (LABEL = 'Confidential - LGPD', INFORMATION_TYPE = 'Pessoa do parceiro (P1)', RANK = MEDIUM);
GO
