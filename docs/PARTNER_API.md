# Guia de uso da API do USPolis para parceiros

Este guia é para quem vai consumir os dados públicos do USPolis (alocações de
salas, prédios, turmas) a partir de outro sistema, por exemplo o site de uma
entidade estudantil. Ele explica como pedir acesso, como usar a sua chave e as
regras de uso, que são parte do acordo para receber a chave.

## 1. Você precisa de uma chave?

| Seu caso | Precisa de chave? |
|---|---|
| Consultar poucas vezes, para testar | **Não.** As rotas públicas aceitam acesso anônimo, com limite por IP. |
| Um **servidor/backend** que consulta a API e serve o seu site | **Sim, chave de servidor.** É o caminho recomendado. |
| Um **site estático** (só HTML/JS) que chama a API direto do navegador | **Sim, chave de navegador**, presa ao domínio do seu site. |

Para pedir uma chave, fale com a equipe do USPolis. Informe:
- nome da entidade;
- nome e e-mail de quem é o contato técnico;
- quais dados você precisa (por exemplo, só alocações);
- se a chave vai ser de servidor ou de navegador e, nesse caso, o domínio do
  site (`https://...`).

Você recebe a chave **uma única vez**, normalmente por um **link de uso
único** enviado ao e-mail de contato (`https://uspolis.com.br/api-key/...`):

1. Abra o link e clique em **Revelar chave**. Abrir a página não gasta o
   link; só o clique em "Revelar" gasta.
2. Copie a chave na hora e guarde-a num local seguro (um gerenciador de
   segredos ou uma variável de ambiente do seu servidor). Depois desse
   clique, o link para de funcionar.
3. O link vale por um tempo limitado (1, 24 ou 72 horas). Se expirar sem
   ser aberto, a chave é cancelada: peça um novo link.
4. **Se o link disser que já foi aberto e não foi você, avise a equipe do
   USPolis na hora.** Alguém pode ter visto a chave antes: ela será
   revogada e uma nova será emitida.

O e-mail traz só o link, nunca a chave. O USPolis guarda apenas uma versão
irreversível (hash) da chave, então não tem como mostrá-la de novo: se você
a perder, ela é revogada e outra é emitida.

## 2. Como usar a chave

Envie a chave no header `X-API-Key`, em requisições **GET**, sempre por
**HTTPS**:

```bash
curl -H "X-API-Key: up_live_..." \
  "https://uspolis.com.br/api/allocations/events?start=2026-10-17&end=2026-10-17"
```

```js
// Backend Node.js (chave de servidor, lida de uma variável de ambiente)
const response = await fetch(
  "https://uspolis.com.br/api/allocations/events?start=2026-10-17&end=2026-10-17",
  { headers: { "X-API-Key": process.env.USPOLIS_API_KEY } },
);
```

**Nunca** coloque a chave na URL (`?api_key=...`): a requisição é recusada
com **400**, porque URLs ficam gravadas em logs e no histórico do navegador.

A chave tem o formato
`up_<ambiente>_<identificador>_<segredo>_<verificador>`, por exemplo
`up_live_a1b2c3d4e5f60718_...`. O ambiente indica onde ela vale:
- `live`: produção;
- `test`: homologação.

Uma chave só funciona no ambiente que a emitiu.

## 3. O que a chave permite

- Só **leitura** (GET/HEAD) e só **rotas públicas**.
- Só as rotas liberadas para a sua chave, por exemplo tudo sob
  `/allocations`. Peça apenas o que for usar.
- Validade de no máximo **1 ano**. Antes de vencer, peça uma chave nova: a
  equipe emite a nova antes de desativar a antiga.

**Limites de consumo:**
- Cada chave tem os seus limites. O padrão para chave de servidor é 30
  requisições a cada 10 s, 120 por minuto e 10.000 por dia.
- **Chave de navegador:** além do limite da chave, cada visitante do seu site
  também tem o próprio limite por IP.

**Intervalos de datas:**
- `/allocations/events` aceita no máximo **31 dias** por requisição.
- As demais rotas aceitam no máximo **1 ano**.
- Para períodos maiores, faça várias requisições.

## 4. Respostas de erro

| Código | Significado | O que fazer |
|---|---|---|
| 400 | Chave na URL, ou intervalo de datas inválido ou longo demais | Mande a chave no header e respeite os tetos de datas |
| 401 | Chave inválida, expirada ou revogada | Confira a chave; se ela vazou ou venceu, peça outra |
| 403 | A chave não tem permissão para esta requisição (rota fora do escopo, método diferente de GET, ou site não autorizado) | Peça o acesso de que precisa |
| 429 | Limite de requisições excedido | Espere o tempo do header `Retry-After` antes de tentar de novo |
| 503 | Chaves temporariamente indisponíveis do nosso lado | Tente mais tarde e avise a equipe se persistir |

Por segurança, as mensagens de 401 e 403 são **genéricas** e não dizem o
motivo exato. Se precisar de ajuda, mande à equipe o **identificador** da
chave (o trecho depois de `up_live_`), **nunca a chave inteira**.

As respostas trazem os headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`
(quantas requisições ainda cabem) e `X-RateLimit-Reset` (segundos até zerar).

## 5. Regras de uso

São parte do acordo. Descumpri-las pode levar à suspensão ou revogação da
chave, sem aviso em caso de abuso.

1. **Chave de servidor fica no servidor.**
   - Nunca coloque em código de front-end, app mobile, repositório,
     print ou ticket.
   - Carregue de uma variável de ambiente ou de um cofre de segredos.
   - Se ela aparecer em um navegador, é recusada (403) e deve ser
     considerada vazada.
2. **Chave de navegador funciona só no domínio cadastrado.** Ela fica visível
   para quem abrir o DevTools, então trate-a como pública e não a use em
   outro lugar.
3. **Faça cache do seu lado.** As alocações mudam pouco. Guarde as respostas
   por pelo menos 5 a 15 minutos e peça intervalos curtos. Melhor ainda: o seu
   backend busca, guarda e serve o seu site.
4. **Respeite o 429.** Espere o `Retry-After`, tente de novo com espera
   exponencial e um pouco de aleatoriedade, e nunca em loop.
5. **Identifique-se:** use um `User-Agent` com o nome da sua aplicação e um
   contato, por exemplo `site-gremio/1.0 (contato@gremio.org)`.
6. **Uma chave por aplicação e por ambiente.** Não compartilhe com outras
   entidades.
7. **Vazou? Avise na hora.** A equipe revoga a chave em segundos e emite
   outra.
8. **Use só o que foi liberado.** Não sonde outras rotas e não raspe dados
   além do escopo combinado.
9. **Dados e LGPD.** Não revenda nem republique dados pessoais. Use os dados
   conforme a LGPD e as políticas da USP.

## 6. Proteja-se contra vazamentos

Configure o seu scanner de segredos (gitleaks, trufflehog, ou padrão
customizado do GitHub) com esta expressão, para ser avisado se a chave for
commitada:

```
\bup_(live|test|dev)_[0-9a-f]{16}_[0-9A-Za-z]{43}_[0-9A-Za-z]{6}\b
```
