# Flask app should start in global layout
import flask
import json
import os
from flask import send_from_directory, request
from flask_ngrok import run_with_ngrok

app = flask.Flask(__name__)
run_with_ngrok(app)


@app.route('/')
@app.route('/home')
def home():
    return "Hello World"


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    query_result = req.get('queryResult')
    query_text = query_result.get('queryText')
    payload = query_result.get('fulfillmentMessages')[0]['payload']
    parameters = query_result.get('parameters')
    intent = query_result.get('intent').get('displayName')
    contexts = query_result.get('outputContexts')

    print(query_result)
    # print("intent: " + str(intent))
    # print("query_text: " + str(query_text))
    # print("payload: " + str(payload))
    # print("parameters: " + str(parameters))
    # print("contexts: " + str(contexts))

    return handle_fulfillments(query_text, payload, parameters, intent, contexts)


def handle_fulfillments(query_text, payload, parameters, intent, contexts):
    try:
        print(intent)
        print(payload)
        intents = {
            '1.1CadastroUsuario': cadastro_usuario,
            '1.1ValidarCpf': validar_cpf,
            '2.2MostrarCardapio': mostrar_cardapio,
            '2.3MostrarCombos': mostrar_combos,
        }

        fulfillment = intents.get(intent, "Invalid intent")
        fulfillment = fulfillment(query_text, payload, parameters, intent, contexts)
        print(fulfillment)
        return fulfillment

    except Exception as ex:
        print(ex)
        return {
            "fulfillmentText": "AAAA",
            "source": "webhookdata"
        }


# Intent 1.1CadastroUsuario
def cadastro_usuario(query_text, payload, parameters, intent, contexts):
    print("1")

    return {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [payload['ok_response']]
                },
            },
            {
                "text": {
                    "text": payload['options']
                },
            }
        ],
        "source": "webhookdata"
    }


# Intent 1.1ValidarCpf
def validar_cpf(query_text, payload, parameters, intent, contexts):
    print("validar_cpf")

    return {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [payload['ok_response']]
                },
            },
            {
                "text": {
                    "text": payload['options']
                },
            }
        ],
        "source": "webhookdata"
    }


# Intent 2.2MostrarCardapio:
def mostrar_cardapio(query_text, payload, parameters, intent, contexts):
    print("mostrar_cardapio")
    temp_cardapio = [
        {"codigo": "001", "sabor": "Mussarela", "preco": 22.00},
        {"codigo": "002", "sabor": "Quatro Queijos", "preco": 28.00},
        {"codigo": "003", "sabor": "Calabresa com cebola", "preco": 26.00},
        {"codigo": "004", "sabor": "Frango com catupiry", "preco": 28.00},
        {"codigo": "005", "sabor": "Atum", "preco": 24.00},
    ]

    cardapio = ['#{} - {} - R${}'.format(str(i['codigo']), str(i['sabor']), str(i['preco'])) for i in temp_cardapio]

    return {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [payload['ok_response']]
                },
            },
            {
                "text": {
                    "text": cardapio
                },
            },
            {
                "text": {
                    "text": ["Escolha uma das opções abaixo:"]
                },
            },
            {
                "text": {
                    "text": payload['options']
                },
            },
        ],
        "source": "webhookdata"
    }


# Intent 2.3MostrarCombos
def mostrar_combos(query_text, payload, parameters, intent, contexts):
    print("mostrar_combos")
    temp_combos = [
        {"codigo": "Chatuba 1", "desc": "1 Pizza Mussarela (grande) + 1 Pizza Calabresa com cebola (grande)", "preco": 32.00},
        {"codigo": "Chatuba 2", "desc": "1 Pizza Frango com catupiry (grande) + 1 Pizza Quatro queijos (grande)", "preco": 34.00},
        {"codigo": "Chatuba 3", "desc": "1 Pizza Mussarela (grande) + 1 Pizza Atum (grande)", "preco": 32.00},
        {"codigo": "Chatubinha 1", "desc": "1 Pizza Mussarela (Broto) + 1 Pizza Calabresa com cebola (Broto)", "preco": 22.00},
    ]
    print(temp_combos)
    combos = ['#{} - {} - R${}'.format(str(i['codigo']), str(i['desc']), str(i['preco'])) for i in temp_combos]
    print(combos)
    return {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [payload['ok_response']]
                },
            },
            {
                "text": {
                    "text": combos
                },
            },
            {
                "text": {
                    "text": ["Escolha uma das opções abaixo:"]
                },
            },
            {
                "text": {
                    "text": payload['options']
                },
            },
        ],
        "source": "webhookdata"
    }


if __name__ == "__main__":
    app.secret_key = 'ItIsASecret'
    app.debug = True
    app.run()
