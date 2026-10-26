// PRM Save · infraestrutura de um ambiente (dev, hml ou prd) em um grupo de recursos.
// Área Partners · TI & Automação · 26/10/2026 · RASCUNHO PARA A TI DA SAVE: não implantado, sem segredos.
// Desenho: docs/prm/v2/04-ti-arquitetura.md.
//
// Escopo: grupo de recursos (um por ambiente: rg-prm-save-dev, rg-prm-save-hml, rg-prm-save-prd).
// Implantar (só a TI, com Owner no grupo, depois de revisar):
//   az deployment group what-if  -g rg-prm-save-hml -f main.bicep -p parametros-hml.exemplo.json
//   az deployment group create   -g rg-prm-save-hml -f main.bicep -p parametros-hml.exemplo.json
//
// O que este arquivo NÃO faz (é passo manual ou da TI, ver §4 do documento):
//   - registros de aplicativo no Entra, papéis, convites B2B, Acesso Condicional;
//   - valores dos segredos no Key Vault (só os nomes são referenciados);
//   - usuário do banco para a identidade da Function (T-SQL: CREATE USER ... FROM EXTERNAL PROVIDER);
//   - CNAME no DNS da Save (o domínio personalizado só é criado quando `dominioPersonalizado` vem preenchido).

targetScope = 'resourceGroup'

// ---------- parâmetros ----------
@description('Ambiente: dev (desenvolvimento), hml (homologação) ou prd (produção).')
@allowed(['dev', 'hml', 'prd'])
param ambiente string

@description('Região dos dados (Function, SQL, Key Vault, Blob, logs). Fica no Brasil por LGPD.')
param local string = 'brazilsouth'

@description('Região do Static Web Apps. Brazil South não aparece na lista de preços do SWA (26/10/2026); o front é só HTML/JS, sem dado de cliente.')
@allowed(['eastus2', 'centralus', 'westus2', 'westeurope', 'eastasia'])
param localSwa string = 'eastus2'

@description('Plano do Static Web Apps. Standard é obrigatório para ligar a Function App própria (backend vinculado).')
@allowed(['Free', 'Standard'])
param skuSwa string = 'Standard'

@description('Banco: gratuito (oferta gratuita serverless, sem SLA; bom para dev/hml), serverless (GP_S_Gen5_1) ou S0 (DTU fixo, recomendado em prd pelo custo previsível).')
@allowed(['gratuito', 'serverless', 'S0'])
param skuSql string = 'S0'

@description('Nome do grupo do Entra que administra o SQL (autenticação só Entra; sem usuário e senha de SQL).')
param sqlAdminGrupoNome string

@description('Object ID do grupo administrador do SQL.')
param sqlAdminGrupoObjectId string

@description('Client ID do registro de aplicativo do portal do parceiro (público, não é segredo). Vazio até a TI criar.')
param prmApiClientId string = ''

@description('Client ID do registro interno da Central (SAVE-SSO-MASTERS). Público, não é segredo.')
param centralApiClientId string = ''

@description('Usa VNet, endpoints privados e DNS privado para SQL, Key Vault e Blob de documentos. Recomendado em prd.')
param redePrivada bool = false

@description('Domínio personalizado (ex.: parceiros.savecompany.com.br). Deixe vazio até o CNAME existir no DNS da Save.')
param dominioPersonalizado string = ''

@description('E-mails que recebem alertas de custo, falha e varredura.')
param emailsAlerta array

@description('Orçamento mensal do grupo de recursos, NA MOEDA DE COBRANÇA da assinatura (USD ou BRL).')
param orcamentoMensal int

@description('Primeiro dia do mês em que o orçamento começa (AAAA-MM-01).')
param inicioOrcamento string

@description('Máximo de instâncias da Function (teto de custo e de abuso). Mínimo aceito pela Microsoft: 1.')
@minValue(1)
@maxValue(100)
param maxInstanciasFunc int = 10

@description('Etiquetas aplicadas a todos os recursos.')
param etiquetas object = {
  sistema: 'prm-save'
  area: 'partners'
  dono: 'luis.melo'
  dados: 'confidencial-lgpd'
}

// ---------- nomes ----------
var sufixo = substring(uniqueString(resourceGroup().id), 0, 6)
var base = 'prm-save-${ambiente}'
var tags = union(etiquetas, { ambiente: ambiente })
var ehPrd = ambiente == 'prd'
var nomeLaw = 'log-${base}'
var nomeAi = 'appi-${base}'
var nomeStFunc = 'stprmfn${ambiente}${sufixo}'
var nomeStDocs = 'stprmdoc${ambiente}${sufixo}'
var nomeKv = 'kv-prm-${ambiente}-${sufixo}'
var nomeSql = 'sql-${base}-${sufixo}'
var nomeDb = 'sqldb-prm'
var nomePlano = 'asp-${base}'
var nomeFunc = 'func-${base}-${sufixo}'
var nomeSwa = 'swa-${base}'
var nomeVnet = 'vnet-${base}'
var containerPacote = 'pacote-app'

// papéis internos do Azure (IDs fixos publicados pela Microsoft)
var papelKvSegredosLeitor = '4633458b-17de-408a-b874-0445c86b69e6' // Key Vault Secrets User
var papelBlobDono = 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b' // Storage Blob Data Owner
var papelBlobColaborador = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe' // Storage Blob Data Contributor
var papelMetricas = '3913510d-42f4-4e42-8a64-420c390055eb' // Monitoring Metrics Publisher

// ---------- observabilidade ----------
resource law 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: nomeLaw
  location: local
  tags: tags
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: ehPrd ? 90 : 30
    workspaceCapping: { dailyQuotaGb: ehPrd ? 1 : json('0.2') } // teto diário: protege o custo de log
  }
}

resource ai 'Microsoft.Insights/components@2020-02-02' = {
  name: nomeAi
  location: local
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: law.id
    IngestionMode: 'LogAnalytics'
    DisableLocalAuth: true // só Entra (identidade gerenciada) envia telemetria
    DisableIpMasking: false // IP do usuário mascarado (LGPD)
  }
}

// ---------- rede privada (opcional) ----------
resource vnet 'Microsoft.Network/virtualNetworks@2024-05-01' = if (redePrivada) {
  name: nomeVnet
  location: local
  tags: tags
  properties: {
    addressSpace: { addressPrefixes: ['10.60.0.0/24'] }
    subnets: [
      {
        name: 'snet-func'
        properties: {
          addressPrefix: '10.60.0.0/26'
          delegations: [{ name: 'flex', properties: { serviceName: 'Microsoft.App/environments' } }]
        }
      }
      {
        name: 'snet-pe'
        properties: { addressPrefix: '10.60.0.64/26', privateEndpointNetworkPolicies: 'Disabled' }
      }
    ]
  }
}
var idSubnetFunc = resourceId('Microsoft.Network/virtualNetworks/subnets', nomeVnet, 'snet-func')
var idSubnetPe = resourceId('Microsoft.Network/virtualNetworks/subnets', nomeVnet, 'snet-pe')

// ---------- armazenamento ----------
// Conta da Function (pacote de implantação e estado interno do host). Sem chave compartilhada: só identidade.
resource stFunc 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: nomeStFunc
  location: local
  tags: tags
  kind: 'StorageV2'
  sku: { name: ehPrd ? 'Standard_ZRS' : 'Standard_LRS' } // ZRS/LRS ficam em Brazil South; GRS replicaria para South Central US
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    supportsHttpsTrafficOnly: true
    defaultToOAuthAuthentication: true
  }
}
resource stFuncBlob 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: stFunc
  name: 'default'
}
resource stFuncPacote 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: stFuncBlob
  name: containerPacote
  properties: { publicAccess: 'None' }
}

// Conta de documentos do PRM (evidências do registro, NF do parceiro, exportações). Só a API lê e grava.
resource stDocs 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: nomeStDocs
  location: local
  tags: tags
  kind: 'StorageV2'
  sku: { name: ehPrd ? 'Standard_ZRS' : 'Standard_LRS' }
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    supportsHttpsTrafficOnly: true
    defaultToOAuthAuthentication: true
    publicNetworkAccess: redePrivada ? 'Disabled' : 'Enabled'
    networkAcls: { defaultAction: redePrivada ? 'Deny' : 'Allow', bypass: 'AzureServices' }
  }
}
resource stDocsBlob 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: stDocs
  name: 'default'
  properties: {
    isVersioningEnabled: true
    deleteRetentionPolicy: { enabled: true, days: 30 } // exclusão a pedido do titular se completa em até 30 dias
    containerDeleteRetentionPolicy: { enabled: true, days: 30 }
  }
}
resource docsContainers 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = [for c in ['evidencias', 'notas-fiscais', 'exportacoes']: {
  parent: stDocsBlob
  name: c
  properties: { publicAccess: 'None' }
}]
resource docsCicloVida 'Microsoft.Storage/storageAccounts/managementPolicies@2023-05-01' = {
  parent: stDocs
  name: 'default'
  properties: {
    policy: {
      rules: [
        {
          name: 'apagar-versoes-antigas'
          enabled: true
          type: 'Lifecycle'
          definition: {
            filters: { blobTypes: ['blockBlob'] }
            actions: { version: { delete: { daysAfterCreationGreaterThan: 30 } } }
          }
        }
        {
          name: 'exportacoes-temporarias'
          enabled: true
          type: 'Lifecycle'
          definition: {
            filters: { blobTypes: ['blockBlob'], prefixMatch: ['exportacoes/'] }
            actions: { baseBlob: { delete: { daysAfterModificationGreaterThan: 7 } } }
          }
        }
      ]
    }
  }
}

// ---------- Key Vault (segredos: token de leitura do HubSpot, sal do índice HMAC) ----------
resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: nomeKv
  location: local
  tags: tags
  properties: {
    tenantId: tenant().tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
    publicNetworkAccess: redePrivada ? 'Disabled' : 'Enabled'
    networkAcls: { defaultAction: redePrivada ? 'Deny' : 'Allow', bypass: 'AzureServices' }
  }
}
// Os segredos NÃO são criados aqui. A TI grava os valores pelo portal (ver §4):
//   hubspot-token-leitura  · app privado "PRM leitura" do HubSpot, só escopos de leitura
//   central-sal            · sal do índice HMAC de negócios ativos (mesmo valor do CENTRAL_SAL das rotinas)

// ---------- Azure SQL (autenticação só Entra) ----------
resource sql 'Microsoft.Sql/servers@2024-05-01-preview' = {
  name: nomeSql
  location: local
  tags: tags
  identity: { type: 'SystemAssigned' }
  properties: {
    minimalTlsVersion: '1.2'
    publicNetworkAccess: redePrivada ? 'Disabled' : 'Enabled'
    administrators: {
      administratorType: 'ActiveDirectory'
      azureADOnlyAuthentication: true
      login: sqlAdminGrupoNome
      sid: sqlAdminGrupoObjectId
      tenantId: tenant().tenantId
      principalType: 'Group'
    }
  }
}
// Sem rede privada: libera só serviços do Azure (a Function sai por IPs dinâmicos). O acesso continua exigindo token Entra.
resource sqlFirewallAzure 'Microsoft.Sql/servers/firewallRules@2024-05-01-preview' = if (!redePrivada) {
  parent: sql
  name: 'AllowAllWindowsAzureIps'
  properties: { startIpAddress: '0.0.0.0', endIpAddress: '0.0.0.0' }
}

var skusSql = {
  gratuito: { name: 'GP_S_Gen5_2', tier: 'GeneralPurpose', family: 'Gen5', capacity: 2 }
  serverless: { name: 'GP_S_Gen5_1', tier: 'GeneralPurpose', family: 'Gen5', capacity: 1 }
  S0: { name: 'S0', tier: 'Standard' }
}
var propsSqlBase = {
  collation: 'Latin1_General_100_CI_AI_SC_UTF8'
  maxSizeBytes: 10737418240 // 10 GB
  requestedBackupStorageRedundancy: ehPrd ? 'Zone' : 'Local' // nunca Geo: a cópia geográfica iria para fora do Brasil
  zoneRedundant: false
}
var propsSqlServerless = skuSql == 'S0' ? {} : { autoPauseDelay: 60, minCapacity: json('0.5') }
var propsSqlGratuito = skuSql == 'gratuito' ? { useFreeLimit: true, freeLimitExhaustionBehavior: 'BillOverUsage' } : {}

resource db 'Microsoft.Sql/servers/databases@2024-05-01-preview' = {
  parent: sql
  name: nomeDb
  location: local
  tags: tags
  sku: skusSql[skuSql]
  properties: union(propsSqlBase, propsSqlServerless, propsSqlGratuito)
}
resource dbRetencaoCurta 'Microsoft.Sql/servers/databases/backupShortTermRetentionPolicies@2024-05-01-preview' = {
  parent: db
  name: 'default'
  properties: { retentionDays: ehPrd ? 35 : 7 }
}
resource dbRetencaoLonga 'Microsoft.Sql/servers/databases/backupLongTermRetentionPolicies@2024-05-01-preview' = if (ehPrd && skuSql != 'gratuito') {
  parent: db
  name: 'default'
  properties: { weeklyRetention: 'P8W', monthlyRetention: 'P12M' } // prazo final depende do parecer de retenção do Jurídico
}
// Auditoria do SQL para o Log Analytics (logins, falhas e lotes executados).
resource sqlAuditoria 'Microsoft.Sql/servers/auditingSettings@2024-05-01-preview' = {
  parent: sql
  name: 'default'
  properties: {
    state: 'Enabled'
    isAzureMonitorTargetEnabled: true
    auditActionsAndGroups: [
      'SUCCESSFUL_DATABASE_AUTHENTICATION_GROUP'
      'FAILED_DATABASE_AUTHENTICATION_GROUP'
      'BATCH_COMPLETED_GROUP'
    ]
  }
}
resource sqlMaster 'Microsoft.Sql/servers/databases@2024-05-01-preview' existing = {
  parent: sql
  name: 'master'
}
resource diagSql 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'auditoria-sql'
  scope: sqlMaster
  properties: {
    workspaceId: law.id
    logs: [{ category: 'SQLSecurityAuditEvents', enabled: true }]
  }
  dependsOn: [sqlAuditoria]
}

// ---------- Function App (Python v2, Flex Consumption, Linux) ----------
resource plano 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: nomePlano
  location: local
  tags: tags
  kind: 'functionapp'
  sku: { tier: 'FlexConsumption', name: 'FC1' }
  properties: { reserved: true }
}

var refKv = '@Microsoft.KeyVault(VaultName=${nomeKv};SecretName='
resource func 'Microsoft.Web/sites@2024-04-01' = {
  name: nomeFunc
  location: local
  tags: tags
  kind: 'functionapp,linux'
  identity: { type: 'SystemAssigned' }
  properties: {
    serverFarmId: plano.id
    httpsOnly: true
    virtualNetworkSubnetId: redePrivada ? idSubnetFunc : null
    functionAppConfig: {
      deployment: {
        storage: {
          type: 'blobContainer'
          value: '${stFunc.properties.primaryEndpoints.blob}${containerPacote}'
          authentication: { type: 'SystemAssignedIdentity' }
        }
      }
      scaleAndConcurrency: { maximumInstanceCount: maxInstanciasFunc, instanceMemoryMB: 2048 }
      runtime: { name: 'python', version: '3.12' }
    }
    siteConfig: {
      minTlsVersion: '1.2'
      ftpsState: 'Disabled'
      http20Enabled: true
      appSettings: [
        { name: 'AzureWebJobsStorage__accountName', value: stFunc.name }
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: ai.properties.ConnectionString }
        { name: 'APPLICATIONINSIGHTS_AUTHENTICATION_STRING', value: 'Authorization=AAD' }
        // Identificadores públicos (não são segredo). Os da Central já existem; o do PRM vem da TI.
        { name: 'CENTRAL_TENANT_ID', value: tenant().tenantId }
        { name: 'CENTRAL_API_CLIENT_ID', value: centralApiClientId }
        { name: 'CENTRAL_SCOPE', value: 'Central.Acesso' }
        { name: 'PRM_API_CLIENT_ID', value: prmApiClientId }
        { name: 'PRM_SCOPE', value: 'Prm.Acesso' }
        { name: 'PRM_AMBIENTE', value: ambiente }
        { name: 'PRM_SQL_SERVIDOR', value: sql.properties.fullyQualifiedDomainName }
        { name: 'PRM_SQL_BANCO', value: nomeDb }
        { name: 'PRM_DOCS_CONTA', value: stDocs.name }
        // Limites da API (ver §2.6 do documento)
        { name: 'PRM_LIMITE_REQ_MINUTO', value: '60' }
        { name: 'PRM_LIMITE_CONSULTAS_DIA', value: '30' }
        { name: 'PRM_LIMITE_REGISTROS_DIA', value: '10' }
        { name: 'CENTRAL_LIMITE_ATIVO', value: '3' }
        // Segredos por referência ao Key Vault (o valor nunca aparece aqui nem no repositório)
        { name: 'HUBSPOT_TOKEN', value: '${refKv}hubspot-token-leitura)' }
        { name: 'CENTRAL_SAL', value: '${refKv}central-sal)' }
        // A sincronização do HubSpot roda em UTC: o Flex Consumption não aceita TZ/WEBSITE_TIME_ZONE.
        { name: 'PRM_SYNC_CRON', value: '0 0 10-22/2 * * 1-5' }
      ]
    }
  }
  dependsOn: [stFuncPacote, vnet]
}

resource diagFunc 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'logs-func'
  scope: func
  properties: {
    workspaceId: law.id
    logs: [{ category: 'FunctionAppLogs', enabled: true }]
  }
}

// Permissões da identidade gerenciada da Function (menor privilégio)
resource rbacFuncPacote 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(stFunc.id, func.id, papelBlobDono)
  scope: stFunc
  properties: { principalId: func.identity.principalId, principalType: 'ServicePrincipal', roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', papelBlobDono) }
}
resource rbacFuncDocs 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(stDocs.id, func.id, papelBlobColaborador)
  scope: stDocs
  properties: { principalId: func.identity.principalId, principalType: 'ServicePrincipal', roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', papelBlobColaborador) }
}
resource rbacFuncKv 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(kv.id, func.id, papelKvSegredosLeitor)
  scope: kv
  properties: { principalId: func.identity.principalId, principalType: 'ServicePrincipal', roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', papelKvSegredosLeitor) }
}
resource rbacFuncAi 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(ai.id, func.id, papelMetricas)
  scope: ai
  properties: { principalId: func.identity.principalId, principalType: 'ServicePrincipal', roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', papelMetricas) }
}

// ---------- Static Web Apps (front do portal e da Central interna) ----------
resource swa 'Microsoft.Web/staticSites@2024-04-01' = {
  name: nomeSwa
  location: localSwa
  tags: tags
  sku: { name: skuSwa, tier: skuSwa }
  properties: {
    allowConfigFileUpdates: true
    stagingEnvironmentPolicy: ehPrd ? 'Disabled' : 'Enabled' // ambientes de PR não usam backend vinculado; em prd ficam desligados
  }
}
// Liga a Function App própria em /api (exige Standard).
resource swaBackend 'Microsoft.Web/staticSites/linkedBackends@2024-04-01' = if (skuSwa == 'Standard') {
  parent: swa
  name: 'backend'
  properties: {
    backendResourceId: func.id
    region: local
  }
}
resource swaDominio 'Microsoft.Web/staticSites/customDomains@2024-04-01' = if (!empty(dominioPersonalizado)) {
  parent: swa
  name: empty(dominioPersonalizado) ? 'sem-dominio' : dominioPersonalizado
  properties: { validationMethod: 'cname-delegation' }
}

// ---------- endpoints privados (opcional) ----------
var zonasPrivadas = [
  { zona: 'privatelink.database.windows.net', alvo: sql.id, grupo: 'sqlServer', nome: 'sql' }
  { zona: 'privatelink.vaultcore.azure.net', alvo: kv.id, grupo: 'vault', nome: 'kv' }
  { zona: 'privatelink.blob.${environment().suffixes.storage}', alvo: stDocs.id, grupo: 'blob', nome: 'docs' }
]
resource dnsPrivado 'Microsoft.Network/privateDnsZones@2020-06-01' = [for z in zonasPrivadas: if (redePrivada) {
  name: z.zona
  location: 'global'
  tags: tags
}]
resource dnsLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = [for (z, i) in zonasPrivadas: if (redePrivada) {
  parent: dnsPrivado[i]
  name: 'link-${nomeVnet}'
  location: 'global'
  properties: { registrationEnabled: false, virtualNetwork: { id: resourceId('Microsoft.Network/virtualNetworks', nomeVnet) } }
  dependsOn: [vnet]
}]
resource pe 'Microsoft.Network/privateEndpoints@2024-05-01' = [for (z, i) in zonasPrivadas: if (redePrivada) {
  name: 'pe-${z.nome}-${base}'
  location: local
  tags: tags
  properties: {
    subnet: { id: idSubnetPe }
    privateLinkServiceConnections: [{ name: z.nome, properties: { privateLinkServiceId: z.alvo, groupIds: [z.grupo] } }]
  }
  dependsOn: [vnet]
}]
resource peDns 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = [for (z, i) in zonasPrivadas: if (redePrivada) {
  parent: pe[i]
  name: 'default'
  properties: { privateDnsZoneConfigs: [{ name: z.nome, properties: { privateDnsZoneId: dnsPrivado[i].id } }] }
}]

// ---------- diagnóstico de acesso a segredos e documentos ----------
resource diagKv 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'auditoria-kv'
  scope: kv
  properties: { workspaceId: law.id, logs: [{ categoryGroup: 'audit', enabled: true }] }
}
resource diagDocs 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'auditoria-docs'
  scope: stDocsBlob
  properties: {
    workspaceId: law.id
    logs: [
      { category: 'StorageRead', enabled: true }
      { category: 'StorageWrite', enabled: true }
      { category: 'StorageDelete', enabled: true }
    ]
  }
}

// ---------- alertas e orçamento ----------
resource grupoAlerta 'Microsoft.Insights/actionGroups@2023-01-01' = {
  name: 'ag-${base}'
  location: 'Global'
  tags: tags
  properties: {
    groupShortName: 'prm${ambiente}'
    enabled: true
    emailReceivers: [for (e, i) in emailsAlerta: { name: 'email${i}', emailAddress: e, useCommonAlertSchema: true }]
  }
}

resource orcamento 'Microsoft.Consumption/budgets@2023-05-01' = {
  name: 'orc-${base}'
  properties: {
    category: 'Cost'
    amount: orcamentoMensal
    timeGrain: 'Monthly'
    timePeriod: { startDate: inicioOrcamento }
    notifications: {
      real50: { enabled: true, operator: 'GreaterThan', threshold: 50, thresholdType: 'Actual', contactEmails: emailsAlerta, contactGroups: [grupoAlerta.id] }
      real80: { enabled: true, operator: 'GreaterThan', threshold: 80, thresholdType: 'Actual', contactEmails: emailsAlerta, contactGroups: [grupoAlerta.id] }
      real100: { enabled: true, operator: 'GreaterThan', threshold: 100, thresholdType: 'Actual', contactEmails: emailsAlerta, contactGroups: [grupoAlerta.id] }
      previsto100: { enabled: true, operator: 'GreaterThan', threshold: 100, thresholdType: 'Forecasted', contactEmails: emailsAlerta, contactGroups: [grupoAlerta.id] }
    }
  }
}

// Falhas da API (5xx e exceções) acima do normal
resource alertaFalhas 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: 'alerta-falhas-${base}'
  location: 'global'
  tags: tags
  properties: {
    severity: 2
    enabled: true
    scopes: [ai.id]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'requisicoes-com-falha'
          criterionType: 'StaticThresholdCriterion'
          metricName: 'requests/failed'
          metricNamespace: 'microsoft.insights/components'
          operator: 'GreaterThan'
          threshold: 10
          timeAggregation: 'Count'
        }
      ]
    }
    actions: [{ actionGroupId: grupoAlerta.id }]
  }
}

// Possível varredura da carteira: evento emitido pela API quando um usuário passa do teto de acertos
resource alertaVarredura 'Microsoft.Insights/scheduledQueryRules@2023-03-15-preview' = {
  name: 'alerta-varredura-${base}'
  location: local
  tags: tags
  kind: 'LogAlert'
  properties: {
    displayName: 'PRM: possível varredura da carteira'
    severity: 1
    enabled: true
    scopes: [law.id]
    evaluationFrequency: 'PT15M'
    windowSize: 'PT1H'
    criteria: {
      allOf: [
        {
          query: 'AppEvents | where Name in ("prm_varredura_suspeita", "prm_teto_diario")'
          timeAggregation: 'Count'
          operator: 'GreaterThan'
          threshold: 0
          failingPeriods: { numberOfEvaluationPeriods: 1, minFailingPeriodsToAlert: 1 }
        }
      ]
    }
    actions: { actionGroups: [grupoAlerta.id] }
  }
}

// Picos de 401/403 (tentativa de acesso indevido ou papel mal atribuído)
resource alertaNegados 'Microsoft.Insights/scheduledQueryRules@2023-03-15-preview' = {
  name: 'alerta-acesso-negado-${base}'
  location: local
  tags: tags
  kind: 'LogAlert'
  properties: {
    displayName: 'PRM: muitos acessos negados (401/403)'
    severity: 2
    enabled: true
    scopes: [law.id]
    evaluationFrequency: 'PT15M'
    windowSize: 'PT1H'
    criteria: {
      allOf: [
        {
          query: 'AppRequests | where ResultCode in ("401", "403", "429")'
          timeAggregation: 'Count'
          operator: 'GreaterThan'
          threshold: 50
          failingPeriods: { numberOfEvaluationPeriods: 1, minFailingPeriodsToAlert: 1 }
        }
      ]
    }
    actions: { actionGroups: [grupoAlerta.id] }
  }
}

// Oferta gratuita do SQL: avisa quando restarem menos de 10 mil segundos de vCore no mês
resource alertaSqlGratuito 'Microsoft.Insights/metricAlerts@2018-03-01' = if (skuSql == 'gratuito') {
  name: 'alerta-sql-gratuito-${base}'
  location: 'global'
  tags: tags
  properties: {
    severity: 3
    enabled: true
    scopes: [db.id]
    evaluationFrequency: 'PT1H'
    windowSize: 'PT1H'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'saldo-gratuito'
          criterionType: 'StaticThresholdCriterion'
          metricName: 'free_amount_remaining'
          metricNamespace: 'Microsoft.Sql/servers/databases'
          operator: 'LessThan'
          threshold: 10000
          timeAggregation: 'Minimum'
        }
      ]
    }
    actions: [{ actionGroupId: grupoAlerta.id }]
  }
}

// ---------- saídas (sem segredos) ----------
output urlSwa string = 'https://${swa.properties.defaultHostname}'
output nomeFunctionApp string = func.name
output principalIdFunction string = func.identity.principalId
output servidorSql string = sql.properties.fullyQualifiedDomainName
output bancoSql string = nomeDb
output nomeKeyVault string = kv.name
output contaDocumentos string = stDocs.name
output proximoPassoSql string = 'No banco ${nomeDb}, como administrador Entra: CREATE USER [${nomeFunc}] FROM EXTERNAL PROVIDER; ALTER ROLE db_datareader ADD MEMBER [${nomeFunc}]; ALTER ROLE db_datawriter ADD MEMBER [${nomeFunc}];'
