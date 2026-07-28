# Guia de Uso para Administradores - Sistema de Triagem HCI

Este guia detalha as funcionalidades administrativas do Sistema de Triagem HCI e como utilizá-las efetivamente.

## Visão Geral

Como administrador do sistema, você tem acesso a funcionalidades exclusivas para gerenciar usuários, visualizar estatísticas e validar triagens realizadas. Este guia aborda todas essas funcionalidades em detalhes.

## Acesso ao Painel Administrativo

1. Acesse a página inicial do sistema: http://localhost:3000
2. Clique no botão "Área Administrativa" no canto superior direito
3. Faça login com suas credenciais de administrador:
   - Usuário: `admin`
   - Senha: `admin` (recomendamos alterar após o primeiro acesso)

## Dashboard Administrativo

O dashboard apresenta uma visão geral do sistema, incluindo:

- Total de triagens realizadas
- Triagens pendentes de validação
- Triagens validadas
- Lista das 5 triagens pendentes mais recentes, com atalho para validar

### Navegação

O menu superior (navbar) dá acesso às seções principais:

- **Dashboard**: Visão geral do sistema
- **Triagens Pendentes**: Lista de triagens aguardando validação
- **Todas as Triagens**: Lista completa de triagens realizadas
- **Sair**: Encerra a sessão administrativa

O gerenciamento de usuários não está no menu — acesse diretamente pela URL
`http://localhost:3000/admin/users`.

## Gerenciamento de Usuários

### Visualizar Usuários

1. Acesse `http://localhost:3000/admin/users`
2. A tabela exibe todos os usuários cadastrados com informações básicas

### Adicionar Novo Usuário

1. Na página de usuários, clique no botão "+ Novo Usuário"
2. Preencha o formulário com os dados do novo usuário:
   - **Nome Completo**: Nome completo do usuário
   - **Nome de Usuário**: Login único para acesso ao sistema
   - **Senha**: Senha inicial (o usuário poderá alterar posteriormente)
   - **Confirmar Senha**: Repetição da senha para confirmação
   - **Email**: Email do usuário para notificações
   - **Função**: Nível de acesso do usuário (Administrador, Médico, Enfermeiro, Recepcionista)
3. Clique em "Cadastrar Usuário" para finalizar

### Editar Usuário

1. Na lista de usuários, clique no botão "Editar" ao lado do usuário desejado
2. Atualize os campos necessários
3. Para alterar a senha, preencha os campos de senha (caso contrário, deixe em branco)
4. Clique em "Salvar Alterações" para confirmar

### Excluir Usuário

1. Na lista de usuários, clique no botão "Excluir" ao lado do usuário desejado
2. Confirme a exclusão na caixa de diálogo
3. **Atenção**: Esta ação não pode ser desfeita

## Validação de Triagens

### Visualizar Triagens Pendentes

1. No menu superior, clique em "Triagens Pendentes" para ver apenas as não validadas,
   ou em "Todas as Triagens" para a lista completa

### Validar uma Triagem

1. Na lista de triagens, selecione a triagem desejada
2. Revise os detalhes da triagem:
   - Sintomas relatados
   - Classificação sugerida pelo sistema
   - Justificativa e condutas recomendadas
3. Escolha uma das opções:
   - **Validar**: Confirma que a classificação sugerida está correta
   - **Ajustar**: Informe a classificação correta antes de validar

4. Adicione um comentário/feedback explicando sua decisão
5. Confirme a validação

### Estatísticas de Validação

O dashboard mostra os contadores de total de triagens, validadas e pendentes
(`GET /api/estatisticas`). Ainda não há gráfico de distribuição por classificação
nem cálculo de precisão por categoria — funcionalidade planejada, não implementada.

## Configurações do Sistema

Ainda não há tela de configurações (nome da instituição, logo, backup/restauração
etc.) implementada no sistema. Essa seção é planejada para uma versão futura.

## Boas Práticas

1. **Segurança**:
   - Altere a senha padrão do administrador
   - Crie contas individuais para cada usuário
   - Revise periodicamente a lista de usuários ativos

2. **Validação de Triagens**:
   - Valide triagens regularmente para melhorar a precisão do sistema
   - Forneça feedback detalhado ao ajustar classificações
   - Monitore as estatísticas de precisão para identificar padrões de erro

3. **Manutenção**:
   - Realize backups semanais do sistema
   - Verifique regularmente o espaço em disco
   - Monitore os logs do sistema para identificar problemas

## Solução de Problemas Comuns

### Usuário não consegue fazer login

1. Verifique se o usuário está digitando as credenciais corretamente
2. Confirme se a conta está ativa na lista de usuários
3. Redefina a senha do usuário se necessário

### Triagem não está sendo processada

1. Verifique se o serviço Ollama está em execução
2. Consulte os logs do backend para identificar erros
3. Reinicie o serviço backend se necessário

### Lentidão no sistema

1. Verifique a utilização de recursos do servidor
2. Considere limpar o banco de dados de triagens antigas
3. Verifique se há muitas requisições simultâneas
