# MikroTik Manager - Sistema Completo

Sistema completo de gerenciamento de roteadores MikroTik com interface web moderna, API REST e integração total com RouterOS.

## 🚀 Módulos Implementados

### ✅ 1. Autenticação e Controle de Acesso
- Login/logout com JWT tokens seguros
- Controle de sessão e timeout automático
- Roles: Admin, Manager, Usuário
- Middleware de proteção de rotas
- Auditoria de login/logout

### ✅ 2. Gerenciamento de Usuários do Sistema
- CRUD completo de usuários
- Controle de status (ativo/inativo)
- Associação many-to-many com empresas
- Histórico de login e tentativas
- Bloqueio automático por tentativas

### ✅ 3. Empresas e Configurações MikroTik
- CRUD de empresas com configurações MikroTik
- Teste de conectividade em tempo real
- Limites padrão por empresa
- Status de conexão monitorado
- Configurações de IP, porta, usuário e senha

### ✅ 4. Perfis e Classes Hotspot
- Criação de perfis por empresa
- Limites de velocidade, tempo e dados
- Configuração de timeouts (idle, session, keepalive)
- Sistema de perfil padrão por empresa
- Controle de ativação/desativação

### ✅ 5. Usuários Hotspot
- CRUD integrado com API MikroTik
- Bloqueio/desbloqueio com motivo
- Monitoramento de usuários online/offline
- Sessões ativas em tempo real
- Controle de expiração e MAC binding

### ✅ 6. Sistema de Créditos
- Tipos: dados, tempo, ilimitado, acumulativo
- Reset automático (diário, semanal, mensal)
- Controle de validade e expiração
- Alertas de crédito baixo
- Histórico de uso detalhado

### ✅ 7. Monitoramento e Relatórios
- Coleta de dados em tempo real
- Relatórios diários, semanais e mensais
- Top usuários por tráfego
- Análise por empresa
- Exportação CSV e JSON

### ✅ 8. Dashboard Interativo
- Estatísticas em tempo real
- Gráficos de uso e performance
- Status de conectividade
- Monitoramento de sistema
- Alertas visuais

### ✅ 9. Administração do Sistema
- Informações de CPU, RAM, Disco
- Logs estruturados e auditoria
- Configurações centralizadas
- Status de saúde do sistema
- Monitoramento de uptime

### ✅ 10. Backup e Restauração
- Backup automático configurável
- Retenção de backups
- Backup manual sob demanda
- Compressão de arquivos
- Verificação de integridade

### ✅ 11. Integração MikroTik
- Conexão via API RouterOS
- Pool de conexões otimizado
- Timeout configurável
- Operações CRUD de usuários
- Sincronização bidirecional

### ✅ 12. Segurança Avançada
- Autenticação JWT robusta
- Rate limiting por endpoint
- Proteção CSRF
- Isolamento de dados por empresa
- Logs de auditoria completos

### ✅ 13. API REST Completa
- Endpoints padronizados
- Documentação automática
- Proteção por token
- Formato JSON consistente
- Códigos de status HTTP corretos

### ✅ 14. Configurações Centralizadas
- Timezone e localização
- Configurações de email SMTP
- Parâmetros MikroTik
- Monitoramento e alertas
- Backup e retenção

### ✅ 15. Containerização Docker
- Dockerfile multi-stage otimizado
- Docker Compose completo
- Volumes persistentes
- Health checks
- Redes isoladas

### ✅ 16. Interface Web Responsiva
- Design moderno com Tailwind CSS
- Componentes shadcn/ui
- Navegação intuitiva
- Tabelas paginadas
- Modais e formulários

### ✅ 17. Sincronização e Cache
- Sincronização MikroTik ↔ Banco
- Cache de relatórios
- Invalidação automática
- Resolução de conflitos
- Performance otimizada

## 🛠 Tecnologias Utilizadas

- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Backend**: Next.js API Routes, Middleware
- **Autenticação**: JWT, Cookies seguros
- **UI Components**: shadcn/ui, Lucide React
- **Banco de Dados**: PostgreSQL (schema completo)
- **Cache**: Redis
- **Proxy**: Nginx com SSL
- **Monitoramento**: Prometheus, Grafana
- **Containerização**: Docker, Docker Compose

## 📦 Estrutura do Projeto

\`\`\`
mikrotik-manager/
├── app/
│   ├── api/                    # API Routes
│   │   ├── auth/              # Autenticação
│   │   ├── companies/         # Empresas
│   │   ├── users/             # Usuários do sistema
│   │   ├── profiles/          # Perfis hotspot
│   │   ├── hotspot-users/     # Usuários hotspot
│   │   ├── credits/           # Sistema de créditos
│   │   ├── reports/           # Relatórios
│   │   ├── settings/          # Configurações
│   │   └── system/            # Status do sistema
│   ├── auth/                  # Páginas de autenticação
│   ├── dashboard/             # Dashboard principal
│   ├── companies/             # Gerenciamento de empresas
│   ├── users/                 # Usuários do sistema
│   ├── profiles/              # Perfis hotspot
│   ├── hotspot-users/         # Usuários hotspot
│   ├── credits/               # Sistema de créditos
│   ├── reports/               # Relatórios
│   └── settings/              # Configurações
├── components/
│   ├── ui/                    # Componentes base
│   └── layout/                # Layouts
├── scripts/
│   └── init-database.sql      # Schema do banco
├── docker-compose.yml         # Orquestração
├── Dockerfile                 # Container da aplicação
├── nginx.conf                 # Configuração do proxy
└── README.md                  # Documentação
\`\`\`

## 🚀 Instalação e Execução

### Pré-requisitos
- Docker e Docker Compose
- Node.js 18+ (para desenvolvimento)

### Instalação Rápida
\`\`\`bash
# Clone o repositório
git clone https://github.com/seu-usuario/mikrotik-manager.git
cd mikrotik-manager

# Inicie todos os serviços
docker-compose up -d

# Acesse a aplicação
# Interface: https://localhost
# API: https://localhost/api
\`\`\`

### Credenciais Demo
- **Admin**: admin@demo.com / admin123
- **Manager**: manager@demo.com / manager123

## 📊 Funcionalidades Principais

### Dashboard em Tempo Real
- Usuários ativos e conectados
- Tráfego de dados (download/upload)
- Status de empresas e roteadores
- Gráficos de performance
- Alertas e notificações

### Gerenciamento Completo
- **Empresas**: Configuração e teste de conectividade
- **Usuários**: Sistema e hotspot com perfis
- **Créditos**: Controle flexível por dados/tempo
- **Relatórios**: Análise detalhada de uso
- **Configurações**: Centralizada e modular

### Integração MikroTik
- Conexão direta via API RouterOS
- Sincronização automática
- Operações em tempo real
- Pool de conexões otimizado
- Tratamento de erros robusto

### Segurança Avançada
- Autenticação JWT com refresh
- Rate limiting inteligente
- Auditoria completa de ações
- Isolamento por empresa
- Criptografia de senhas

## 🔧 Configuração Avançada

### Variáveis de Ambiente
\`\`\`env
# Aplicação
NODE_ENV=production
JWT_SECRET=your-super-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/mikrotik_manager
REDIS_URL=redis://localhost:6379

# MikroTik
MIKROTIK_DEFAULT_PORT=8728
MIKROTIK_CONNECTION_TIMEOUT=10

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
\`\`\`

### Configuração SSL
Para produção, adicione seus certificados:
\`\`\`bash
mkdir ssl
# Adicione cert.pem e key.pem
\`\`\`

## 📈 Monitoramento

### Métricas Disponíveis
- **Sistema**: CPU, Memória, Disco, Uptime
- **Aplicação**: Requests/s, Response time, Errors
- **MikroTik**: Conexões ativas, Status dos roteadores
- **Usuários**: Sessions ativas, Tráfego, Créditos

### Alertas Configuráveis
- Falha de conexão MikroTik
- Alto uso de recursos
- Créditos baixos
- Tentativas de login suspeitas

## 🔄 Backup e Restauração

### Backup Automático
\`\`\`bash
# Configurar backup diário às 2:00
# Via interface web ou API
POST /api/backup/schedule
\`\`\`

### Restauração
\`\`\`bash
# Restaurar backup específico
POST /api/backup/restore
{
  "backupFile": "backup-2024-01-31.sql.gz"
}
\`\`\`

## 🧪 Testes

\`\`\`bash
# Testes unitários
npm run test

# Testes de integração
npm run test:integration

# Coverage completo
npm run test:coverage
\`\`\`

## 🚀 Deploy em Produção

### Docker Swarm
\`\`\`bash
docker swarm init
docker stack deploy -c docker-compose.prod.yml mikrotik-manager
\`\`\`

### Kubernetes
\`\`\`bash
kubectl apply -f k8s/
\`\`\`

## 📝 API Documentation

### Endpoints Principais

#### Autenticação
\`\`\`bash
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/refresh
\`\`\`

#### Empresas
\`\`\`bash
GET    /api/companies
POST   /api/companies
PUT    /api/companies/{id}
DELETE /api/companies/{id}
POST   /api/companies/{id}/test-connection
\`\`\`

#### Usuários Hotspot
\`\`\`bash
GET    /api/hotspot-users
POST   /api/hotspot-users
PUT    /api/hotspot-users/{id}
DELETE /api/hotspot-users/{id}
POST   /api/hotspot-users/{id}/block
POST   /api/hotspot-users/{id}/disconnect
\`\`\`

#### Créditos
\`\`\`bash
GET    /api/credits
POST   /api/credits
PUT    /api/credits/{id}
DELETE /api/credits/{id}
POST   /api/credits/{id}/reset
\`\`\`

#### Relatórios
\`\`\`bash
GET /api/reports?startDate=2024-01-01&endDate=2024-01-31&company=all&type=daily
GET /api/reports/export?format=csv
\`\`\`

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License.

## 🆘 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/mikrotik-manager/issues)
- **Documentação**: [Wiki](https://github.com/seu-usuario/mikrotik-manager/wiki)
- **Email**: suporte@mikrotik-manager.com

---

**MikroTik Manager** - Sistema profissional completo para gerenciamento de roteadores MikroTik com interface web moderna, API REST robusta e integração total com RouterOS.
