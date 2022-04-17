# Cliente torrent de terminal
## Descrição
Este repositório contém um cliente torrent simples para ser executado em terminal.

## Executando o programa
Para executar o programa você deve ter o (poetry)[https://python-poetry.org/] instalado.

Em seguida, na pasta do projeto execute o comando abaixo para criar um ambiente virtual python de execução do projeto:

```
poetry shell
```

Então, instale as dependências de projeto:

```
poetry install
```

E execute o projeto com:

```
python bcli.py <Caminho do arquivo .torrent>
```

Um arquivo de teste já foi incluido na pasta 'arquivos de teste'

## Problemas de execução atuais
Uma das bibliotecas (bencode.py) não está decodificando o arquivo .torrent corretamente, então não é possível acessar as informações do arquivo torrent.

## Agradecimentos

Este projeto é baseado no [cliente bittorrent](https://github.com/kcchik/bittorrent-client) feito pelo usuário [kcchik](https://github.com/kcchik).

**This project is based on the [bittorrent client](https://github.com/kcchik/bittorrent-client) developed by [kcchik](https://github.com/kcchik). Thank you!!**