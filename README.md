<h3 align="center">Database API</h3>

> [!NOTE]
> Atualização: nesta branch, toda API foi implementada com websockets para suprir certas necessidades do meu projeto privado.
>   
> Está API não está totalmente completa, há certos pontos que ainda preciso resolver ao longo do tempo nela.

## Referências

- [Sobre o projeto](#about)
- [Explicações](#exp)
- [API](#api)
- [Getgen/Postgen (twcode 1)](#api-1)
- [Getpy/Postpy (twcode 2)](#api-2)
- [Heartbeat (twcode 3)](#api-3)
- [Get (twcode 4)](#api-4)
- [Post (twcode 5)](#api-5)
- [Delete (twcode 6)](#api-6)



## Sobre este repositório <a id = "about"></a>

Este repositório contém a implementação de uma API desenvolvida para um projeto privado. Seu objetivo é fornecer uma interface estruturada e segura para comunicação entre diferentes partes do sistema, permitindo a manipulação e o acesso controlado aos dados e funcionalidades da aplicação.

## Sobre a API <a id = "exp"></a>

- Esta documentação explicaria como utilizar minha API WebSocket para comunicação em tempo real entre aplicações.

## API <a id = "api"></a>

Está API funciona semelhante a mesma API em websockets do app "Discord". Exemplo abaixo:

- OBS: Certas partes onde tiver "..." eu não vou explicar muito oque realmente seria para não fujir do assunto principal.

```python
# Exemplo básico de body a ser enviada para API. Aqui estamos utilizando o heartbeat.
{
***REMOVED***"tw": 3,
***REMOVED***"dt": {
***REMOVED***"git_url": "..."
***REMOVED***}
}
```

caso enviado, retornaria:

```python
{
***REMOVED***"tw": 0,
***REMOVED***"dt": {
***REMOVED***"ok": True
***REMOVED***}
}
```
- ## Get (twcode 4) <a id = "api-4"></a>

Este twcode retorna informações sobre uma ou todas rows da database.

```python
{
***REMOVED***"tw": 4,
***REMOVED***"dt": {  #dt aqui pode ser None ou um json.
***REMOVED***"git_url": "...", #está key não é obrigatória.
***REMOVED***"arg": True  #ou False. Está é obrigatória caso "dt" seja um json.
***REMOVED***}
}
```

Response:

```python
{
***REMOVED***"tw": 0,
***REMOVED***"dt": {
***REMOVED***"ok": True, 
***REMOVED***"result": list({
***REMOVED******REMOVED***"id": "...",
***REMOVED******REMOVED***"git_url":"...",
***REMOVED******REMOVED***"email": "...",
***REMOVED******REMOVED***"ssh_key": "...", # ou None. Depende do seu "arg" no body.
***REMOVED******REMOVED***"priv_key":"...", # ou None. Depende do seu "arg" no body.
***REMOVED******REMOVED***"password":"...",
***REMOVED******REMOVED***"time": "...",
***REMOVED******REMOVED***"heartbeat": "..."
***REMOVED***})
***REMOVED***}
}
```

- ## Post (twcode 5) <a id = "api-5"></a>

Este twcode adicona uma nova row na database.

```python
{
***REMOVED***"tw": 5,
***REMOVED***"dt": {
***REMOVED***"git_url": "...",
***REMOVED***"ssh_key": "...",
***REMOVED***"priv_key": "...",
***REMOVED***"email": "...", 
***REMOVED***"password": "...",
***REMOVED***}
}
```

Response:

```python
{
***REMOVED***"tw": 0,
***REMOVED***"dt": {
***REMOVED***"ok": True, 
***REMOVED***"id": "..." #id referente a row criada na database.
***REMOVED***}
}
```

- ## Delete (twcode 6) <a id = "api-6"></a>

Este twcode remove alguma row específica da database.

```python
{
***REMOVED***"tw": 6,
***REMOVED***"dt": {
***REMOVED***"git_url": "..."
***REMOVED***}
}
```

Response:

```python
{
***REMOVED***"tw": 0,
***REMOVED***"dt": {
***REMOVED***"ok": True, 
***REMOVED***"id": "..." #id referente a row deletada na database.
***REMOVED***}
}
```

- ## Heartbeat (twcode 3) <a id = "api-3"></a>

Este twcode fica responsável por enviar um timestamp à row do container selecioando com objetivo de mostrar que o container ainda está de pé.

```python
{
***REMOVED***"tw": 3,
***REMOVED***"dt": {
***REMOVED***"git_url": "..."
***REMOVED***}
}
```

Response:

```python
{
***REMOVED***"tw": 0,
***REMOVED***"dt": {
***REMOVED***"ok": True
***REMOVED***}
}
```


- ## Getgen/Postgen (twcode 1) <a id = "api-1"></a>

Este twcode sustenta o método de criação de novos containers

- #### Postgen

Este método lida de editar/criar o json que lidará com a criação de novos containers.

```python
{
***REMOVED***"tw": 1,
***REMOVED***"dt": {
***REMOVED***"create": True,
***REMOVED***"vms": int, #números de containers a ser criado
***REMOVED***}
}
```

Response:

```python
{
***REMOVED***"tw": 0,
***REMOVED***"dt": {
***REMOVED***{
***REMOVED******REMOVED***"ok": True,
***REMOVED******REMOVED***"All": False,
***REMOVED******REMOVED***"result": "Solicitada a criação de ... containers!"
***REMOVED***}
***REMOVED***}
}
```

- #### Getgen 

Este método retorna o json criado pelo método Postgen.

```python
{
***REMOVED***"tw": 1,
***REMOVED***"dt": {
***REMOVED***"verif": bool
***REMOVED***}
}
```

Response caso o "verif" `False`:

```python
{
***REMOVED***"tw": 0,
***REMOVED***"dt": {
***REMOVED***"ok": True, 
***REMOVED***"result": {
***REMOVED******REMOVED***"data": {
***REMOVED******REMOVED***"create": bool,
***REMOVED******REMOVED***"finished": "...",
***REMOVED******REMOVED***"info": {
***REMOVED******REMOVED******REMOVED***"created": int,
***REMOVED******REMOVED******REMOVED***"request": int,
***REMOVED******REMOVED******REMOVED***"started": timestamp
***REMOVED******REMOVED***}
***REMOVED******REMOVED***}
***REMOVED***}
***REMOVED***}
}
```

Response caso o "verif" `True`:

```python
{
***REMOVED***"tw": 0,
***REMOVED***"dt": {
***REMOVED***"ok": True, 
***REMOVED***"result": "... containers criados no momento." # Ou "Todos containers solicitados já criados!"
***REMOVED***}
}
```
- ## Getpy/Postpy (twcode 2) <a id = "api-2"></a>

Este twcode envia seu código python para sandbox dos containers.

- #### Postpy

Este método retorna o resultado da sandbox do container.

```python
{
***REMOVED***"tw": 2,
***REMOVED***"dt": {
***REMOVED***"code": "..." # seu código ai.
***REMOVED***"package": "..." #suas packages. Pode ser None tambem.
***REMOVED***"amount": int,
***REMOVED***"edit": None,
***REMOVED***}
}
```

Response:

```python
{
***REMOVED***"tw": 0,
***REMOVED***"dt": {
***REMOVED***{
***REMOVED***"ok": True, 
***REMOVED******REMOVED***"result": "Sucess: Seu codigo estará rodando em ... containers!"
***REMOVED***}
***REMOVED***}
}
```

- #### Getpy

Este método retorna o resultado da sandbox do container.

```python
{
***REMOVED***"tw": 2,
***REMOVED***"dt": None
}
```

Response:

```python
{
***REMOVED***"tw": 0,
***REMOVED***"dt": {
***REMOVED***"ok": True, 
***REMOVED***"result": {...}
***REMOVED***}
}
```