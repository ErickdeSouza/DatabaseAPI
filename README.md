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
"tw": 3,
    "dt": {
        "git_url": "..."
    }
}
```

caso enviado, retornaria:

```python
{
    "tw": 0,
    "dt": {
        "ok": True
    }
}
```
- ## Get (twcode 4) <a id = "api-4"></a>

Este twcode retorna informações sobre uma ou todas rows da database.

```python
{
    "tw": 4,
    "dt": {  #dt aqui pode ser None ou um json.
        "git_url": "...", #está key não é obrigatória.
        "arg": True  #ou False. Está é obrigatória caso "dt" seja um json.
    }
}
```

Response:

```python
{
    "tw": 0,
    "dt": {
        "ok": True, 
        "result": list({
            "id": "...",
            "git_url":"...",
            "email": "...",
            "ssh_key": "...", # ou None. Depende do seu "arg" no body.
            "priv_key":"...", # ou None. Depende do seu "arg" no body.
            "password":"...",
            "time": "...",
            "heartbeat": "..."
        })
    }
}
```

- ## Post (twcode 5) <a id = "api-5"></a>

Este twcode adicona uma nova row na database.

```python
{
    "tw": 5,
    "dt": {
        "git_url": "...",
        "ssh_key": "...",
        "priv_key": "...",
        "email": "...", 
        "password": "...",
    }
}
```

Response:

```python
{
    "tw": 0,
    "dt": {
        "ok": True, 
        "id": "..." #id referente a row criada na database.
    }
}
```

- ## Delete (twcode 6) <a id = "api-6"></a>

Este twcode remove alguma row específica da database.

```python
{
    "tw": 6,
    "dt": {
        "git_url": "..."
    }
}
```

Response:

```python
{
    "tw": 0,
    "dt": {
        "ok": True, 
        "id": "..." #id referente a row deletada na database.
    }
}
```

- ## Heartbeat (twcode 3) <a id = "api-3"></a>

Este twcode fica responsável por enviar um timestamp à row do container selecioando com objetivo de mostrar que o container ainda está de pé.

```python
{
    "tw": 3,
        "dt": {
        "git_url": "..."
    }
}
```

Response:

```python
{
    "tw": 0,
        "dt": {
        "ok": True
    }
}
```


- ## Getgen/Postgen (twcode 1) <a id = "api-1"></a>

Este twcode sustenta o método de criação de novos containers

- #### Postgen

Este método lida de editar/criar o json que lidará com a criação de novos containers.

```python
{
    "tw": 1,
    "dt": {
        "method": "POST",
        "create": True,
        "vms": int, #números de containers a ser criado
    }
}
```

Response:

```python
{
    "tw": 0,
    "dt": {
        "ok": True,
        "All": False,
        "result": "Solicitada a criação de ... containers!"
    }
}
```

- #### Getgen 

Este método retorna o json criado pelo método Postgen.

```python
{
    "tw": 1,
    "dt": {
        "method": "GET",
        "verif": bool
    }
}
```

Response caso o "verif" `False`:

```python
{
    "tw": 0,
    "dt": {
        "ok": True, 
        "result": {
            "data": {
                "create": bool,
                "finished": "...",
                "info": {
                    "created": int,
                    "request": int,
                    "started": timestamp
                }
            }
        }
    }
}
```

Response caso o "verif" `True`:

```python
{
    "tw": 0,
    "dt": {
        "ok": True, 
        "result": "... containers criados no momento." # Ou "Todos containers solicitados já criados!"
    }
}
```
- ## Getpy/Postpy (twcode 2) <a id = "api-2"></a>

Este twcode envia seu código python para sandbox dos containers.

- #### Postpy

Este método retorna o resultado da sandbox do container.

```python
{
    "tw": 2,
    "dt": {
        "method": "POST",
        "code": "..." # seu código ai.
        "package": "..." #suas packages. Pode ser None tambem.
        "amount": int,
        "edit": None,
    }
}
```

Response:

```python
{
    "tw": 0,
    "dt": {
        "ok": True, 
        "result": "Sucess: Seu codigo estará rodando em ... containers!"
    }
}
```

- #### Getpy

Este método retorna o resultado da sandbox do container.

```python
{
    "tw": 2,
    "dt": {
        "method": "GET"
    }
}
```

Response:

```python
{
    "tw": 0,
    "dt": {
        "ok": True, 
        "result": {...}
    }
}
```