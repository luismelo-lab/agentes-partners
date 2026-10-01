#!/bin/zsh
# Liga (ou religa) os horários automáticos do terminal. Para desligar um: launchctl bootout gui/$(id -u)/<label>
D="$HOME/agentes-partners/infra/launchd"; L="$HOME/Library/LaunchAgents"; mkdir -p "$L" "$HOME/agentes-partners/logs"
for f in "$D"/com.savecompany.partners.*.plist; do
  n=$(basename "$f" .plist); launchctl bootout gui/$(id -u)/$n 2>/dev/null
  cp "$f" "$L/" && launchctl bootstrap gui/$(id -u) "$L/$n.plist" && echo "ligado: $n"
done
