
# PATH
export PATH="$PATH:$HOME/.local/bin"

# ENV vars
export SSH_AUTH_SOCK="$XDG_RUNTIME_DIR/ssh-agent.socket"

# SSH
ssh-add ~/.ssh/github >/dev/null 2>&1

# CARBON
source ~/.carbon/env
