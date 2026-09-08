# Single base image used by every task. Installs every app tool we
# evaluate (apify CLI, gh CLI, ntn CLI, linear CLI, mcp-remote, @apify/mcpc,
# mcporter, IBM mcp-cli, notion MCP server, playwright-mcp + chromium) plus
# stdio proxies for the remote MCPs. Connector selection happens at
# runtime (which mcp_servers / instructions / setup scripts the agent gets) -
# the image is fixed, so its dirhash is stable and the sandbox template cache
# stays hot across runs.

# node:24 (not 22): mcporter requires node >= 24.
FROM node:24-bookworm

# gh CLI
ARG GH_VERSION=2.78.0
RUN ARCH=$(dpkg --print-architecture) \
 && curl -fsSL "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_${ARCH}.deb" -o /tmp/gh.deb \
 && apt-get update && apt-get install -y --no-install-recommends /tmp/gh.deb \
 && rm /tmp/gh.deb && rm -rf /var/lib/apt/lists/*

# Node-based CLIs. `command -v` asserts each bin lands on PATH so a broken
# build fails loudly instead of the agent silently falling back to curl.
RUN npm install -g apify-cli@1.6.2 mcp-remote@0.1.38 @apify/mcpc@0.3.0 mcporter@0.13.10 \
      ntn@0.23.2 @notionhq/notion-mcp-server@2.5.1 @schpet/linear-cli@2.6.0 \
 && command -v apify && command -v mcp-remote && command -v mcpc && command -v mcporter \
 && command -v ntn && command -v notion-mcp-server && command -v linear

# Playwright MCP + headless Chromium (browser connector). Browser installed via
# the package's own bundled playwright so the revision matches; --with-deps
# pulls chromium's OS libs via apt.
RUN npm install -g @playwright/mcp@0.0.80 \
 && command -v playwright-mcp \
 && cd /usr/local/lib/node_modules/@playwright/mcp \
 && npx playwright install --with-deps chromium

# IBM mcp-cli (Python; bookworm ships 3.11, PEP 668 needs --break-system-packages).
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip \
 && rm -rf /var/lib/apt/lists/* \
 && pip3 install --break-system-packages mcp-cli==0.20.1 \
 && command -v mcp-cli

# Stdio shims for remote MCPs (harbor's MCPServerConfig has no `headers` field).
COPY apify-mcp-proxy.sh /usr/local/bin/apify-mcp-proxy
COPY github-mcp-proxy.sh /usr/local/bin/github-mcp-proxy
COPY notion-mcp-proxy.sh /usr/local/bin/notion-mcp-proxy
COPY notion-fixtures-probe.sh /usr/local/bin/notion-fixtures-probe
COPY linear-mcp-proxy.sh /usr/local/bin/linear-mcp-proxy
COPY linear-fixtures-probe.sh /usr/local/bin/linear-fixtures-probe
COPY mcp-stdio-probe.py /usr/local/bin/mcp-stdio-probe
COPY mcpc-probe.sh /usr/local/bin/mcpc-probe
COPY mcporter-probe.sh /usr/local/bin/mcporter-probe
COPY mcp-cli-probe.sh /usr/local/bin/mcp-cli-probe
RUN chmod +x /usr/local/bin/apify-mcp-proxy /usr/local/bin/github-mcp-proxy \
              /usr/local/bin/notion-mcp-proxy /usr/local/bin/notion-fixtures-probe \
              /usr/local/bin/linear-mcp-proxy /usr/local/bin/linear-fixtures-probe \
              /usr/local/bin/mcp-stdio-probe /usr/local/bin/mcpc-probe \
              /usr/local/bin/mcporter-probe /usr/local/bin/mcp-cli-probe

WORKDIR /app
