# Flask app should start in global layout
import flask
import json
import os
from flask import send_from_directory, request
from flask_ngrok import run_with_ngrok

app = flask.Flask(__name__)
#run_with_ngrok(app)

cardapio = {
    "pizzas":[
        {"codigo": "001", "desc": "Mussarela", "preco": 22.00},
        {"codigo": "002", "desc": "Quatro Queijos", "preco": 28.00},
        {"codigo": "003", "desc": "Calabresa com cebola", "preco": 26.00},
        {"codigo": "004", "desc": "Frango com catupiry", "preco": 28.00},
        {"codigo": "005", "desc": "Atum", "preco": 24.00},
    ],
    "combos": [
        {"codigo": "Chatuba 1", "desc": "1 Pizza Mussarela (grande) + 1 Pizza Calabresa com cebola (grande)", "preco": 32.00},
        {"codigo": "Chatuba 2", "desc": "1 Pizza Frango com catupiry (grande) + 1 Pizza Quatro queijos (grande)", "preco": 34.00},
        {"codigo": "Chatuba 3", "desc": "1 Pizza Mussarela (grande) + 1 Pizza Atum (grande)", "preco": 32.00},
        {"codigo": "Chatubinha 1", "desc": "1 Pizza Mussarela (Broto) + 1 Pizza Calabresa com cebola (Broto)", "preco": 22.00},
    ],
    "cupons": [
        {"codigo": "CH4TUB410", "desconto": 0.1}
    ]
}


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
    session = req.get('session')

    print(query_result)
    # print("session: " + str(session))
    # print("intent: " + str(intent))
    # print("query_text: " + str(query_text))
    # print("payload: " + str(payload))
    # print("parameters: " + str(parameters))
    # print("contexts: " + str(contexts))

    return handle_fulfillments(query_text, payload, parameters, intent, contexts, session)


def handle_fulfillments(query_text, payload, parameters, intent, contexts, session):
    try:
        print(intent)
        print(payload)
        intents = {
            '1.1CadastroUsuario': cadastro_usuario,
            '1.1ValidarCpf': validar_cpf,
            '2.1.2InformaCodigoPizza': informa_codigo_pizza,
            '2.1.2InformaCodigoCombo': informa_codigo_combos,
            '2.4.1InformaCodigoCupom': informa_codigo_cupom,
            '2.2MostrarCardapio': mostrar_cardapio,
            '2.3MostrarCombos': mostrar_combos,
            '2.5FinalizarPedido': finaliza_pedido,
            '2.5CancelarPedido': cancela_pedido
        }

        fulfillment = intents.get(intent, "Invalid intent")
        fulfillment = fulfillment(query_text, payload, parameters, intent, contexts, session)
        print(fulfillment)
        return fulfillment

    except Exception as ex:
        print(ex)
        return {
            "fulfillmentText": "Desculpe não compreendi, tente novamente.",
            "source": "webhookdata"
        }


# Intent 1.1CadastroUsuario
def cadastro_usuario(query_text, payload, parameters, intent, contexts, session):
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
        "outputContexts": [
            {
                "name": "{}/contexts/pedido".format(session),
                "lifespanCount": 99,
                "parameters": {
                    "pedido": {
                        "itens": [],
                        "cupom": []
                    }
                }
            }
        ],
        "source": "webhookdata"
    }


# Intent 1.1ValidarCpf
def validar_cpf(query_text, payload, parameters, intent, contexts, session):
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
        "outputContexts": [
            {
                "name": "{}/contexts/pedido".format(session),
                "lifespanCount": 99,
                "parameters": {
                    "pedido": {
                        "itens": [],
                        "cupom": []
                    }
                }
            }
        ],
        "source": "webhookdata"
    }


# Intent 2.1.2InformaCodigoPizza
def informa_codigo_pizza(query_text, payload, parameters, intent, contexts, session):
    print("Informa codigo pizza")
    print(contexts)

    ctxPedido = list(filter(lambda ctx: "/contexts/pedido" in ctx["name"], contexts))
    ctxItem = ctxPedido[0]["parameters"]["pedido"]["itens"]
    ctxCupom = ctxPedido[0]["parameters"]["pedido"]["cupom"]

    array_codigo_pizza = [c["codigo"] for c in cardapio["pizzas"]]

    if parameters["codigo"] in array_codigo_pizza:
        pizza = list(filter(lambda p: p["codigo"] == parameters["codigo"], cardapio["pizzas"]))
        pizza[0]["type"] = 1
        ctxItem.append(pizza[0])

        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [payload['ok_response'].format(str(pizza[0]["desc"]))]
                    },
                },
                {
                    "text": {
                        "text": ["Escolha uma opção:"]
                    },
                },
                {
                    "text": {
                        "text": payload['options']
                    },
                }
            ],
            "outputContexts": [
                {
                    "name": "{}/contexts/pedido".format(session),
                    "lifespanCount": 99,
                    "parameters": {
                        "pedido": {
                            "itens": ctxItem,
                            "cupom": ctxCupom
                        }
                    }
                },
                {
                    "name": "{}/contexts/menu-opcoes".format(session),
                    "lifespanCount": 3,
                    "parameters": {}
                },
                {
                    "name": "{}/contexts/adicionar-pizza".format(session),
                    "lifespanCount": 0,
                    "parameters": {}
                }
            ],
            "source": "webhookdata"
        }

    else:
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [payload["not_found"]]
                    }
                },
            ],
            "source": "webhookdata"
        }


# Intent 2.1.2InformaCodigoCombos
def informa_codigo_combos(query_text, payload, parameters, intent, contexts, session):
    print("Informa codigo combos")
    print(contexts)

    ctxPedido = list(filter(lambda ctx: "/contexts/pedido" in ctx["name"], contexts))
    ctxItem = ctxPedido[0]["parameters"]["pedido"]["itens"]
    ctxCupom = ctxPedido[0]["parameters"]["pedido"]["cupom"]

    array_codigo_combos = [c["codigo"] for c in cardapio["combos"]]

    if parameters["codigo"] in array_codigo_combos:
        combo = list(filter(lambda c: c["codigo"] == parameters["codigo"], cardapio["combos"]))
        combo[0]["type"] = 2
        ctxItem.append(combo[0])

        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [payload['ok_response'].format(str(combo[0]["desc"]))]
                    },
                },
                {
                    "text": {
                        "text": ["Escolha uma opção:"]
                    },
                },
                {
                    "text": {
                        "text": payload['options']
                    },
                }
            ],
            "outputContexts":  [
                {
                    "name": "{}/contexts/pedido".format(session),
                    "lifespanCount": 99,
                    "parameters": {
                        "pedido": {
                            "itens": ctxItem,
                            "cupom": ctxCupom
                        }
                    }
                },
                {
                    "name": "{}/contexts/menu-opcoes".format(session),
                    "lifespanCount": 3,
                    "parameters": {}
                },
                {
                    "name": "{}/contexts/adicionar-combo".format(session),
                    "lifespanCount": 0,
                    "parameters": {}
                }
            ],

            "source": "webhookdata"
        }

    else:
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [payload["not_found"]]
                    }
                },
            ],
            "source": "webhookdata"
        }


# Intent 2.4.1InformaCodigoCupom
def informa_codigo_cupom(query_text, payload, parameters, intent, contexts, session):
    print("Informa codigo cupom")
    print(contexts)

    ctxPedido = list(filter(lambda ctx: "/contexts/pedido" in ctx["name"], contexts))
    ctxItem = ctxPedido[0]["parameters"]["pedido"]["itens"]
    ctxCupom = ctxPedido[0]["parameters"]["pedido"]["cupom"]

    if len(ctxCupom) > 0:
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": ["Seu pedido já possui um cupom aplicado!"]
                    },
                },
                {
                    "text": {
                        "text": ["Escolha uma opção:"]
                    },
                },
                {
                    "text": {
                        "text": payload["options"]
                    },
                }
            ],
            "outputContexts":  [
                {
                    "name": "{}/contexts/menu-opcoes".format(session),
                    "lifespanCount": 3,
                    "parameters": {}
                },
                {
                    "name": "{}/contexts/codigo-cupom".format(session),
                    "lifespanCount": 0,
                    "parameters": {}
                }
            ],
            "source": "webhookdata"
        }

    else:
        array_codigo_cupons = [c["codigo"] for c in cardapio["cupons"]]
        if parameters["codigo"] in array_codigo_cupons:
            cupom = list(filter(lambda c: c["codigo"] == parameters["codigo"], cardapio["cupons"]))
            ctxCupom.append(cupom[0])

            return {
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [payload["ok_response"].format(str(cupom[0]["codigo"]))]
                        },
                    },
                    {
                        "text": {
                            "text": ["Escolha uma opção:"]
                        },
                    },
                    {
                        "text": {
                            "text": payload["options"]
                        },
                    }
                ],
                "outputContexts": [
                    {
                        "name": "{}/contexts/pedido".format(session),
                        "lifespanCount": 99,
                        "parameters": {
                            "pedido": {
                                "itens": ctxItem,
                                "cupom": ctxCupom
                            }
                        }
                    },
                    {
                        "name": "{}/contexts/menu-opcoes".format(session),
                        "lifespanCount": 3,
                        "parameters": {}
                    },
                    {
                        "name": "{}/contexts/codigo-cupom".format(session),
                        "lifespanCount": 0,
                        "parameters": {}
                    }
                ],
                "source": "webhookdata"
            }

        else:
            return {
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [payload["not_found"]]
                        },
                    },
                    {
                        "text": {
                            "text": ["Escolha uma opção:"]
                        },
                    },
                    {
                        "text": {
                            "text": payload["options"]
                        },
                    }
                ],
                "outputContexts": [
                    {
                        "name": "{}/contexts/menu-opcoes".format(session),
                        "lifespanCount": 3,
                        "parameters": {}
                    },
                    {
                        "name": "{}/contexts/codigo-cupom".format(session),
                        "lifespanCount": 0,
                        "parameters": {}
                    }
                ],
                "source": "webhookdata"
            }


# Intent 2.2MostrarCardapio:
def mostrar_cardapio(query_text, payload, parameters, intent, contexts, session):
    print("mostrar_cardapio")

    pizzas = ['#{} - {} - R${}'.format(str(i['codigo']), str(i['desc']), str(i['preco'])) for i in cardapio["pizzas"]]

    return {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [payload['ok_response']]
                },
            },
            {
                "text": {
                    "text": pizzas
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
def mostrar_combos(query_text, payload, parameters, intent, contexts, session):
    print("mostrar_combos")

    combos = ['#{} - {} - R${}'.format(str(i['codigo']), str(i['desc']), str(i['preco'])) for i in cardapio["combos"]]

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


# Intent 2.4CodigoCupom
def codigo_cupom(query_text, payload, parameters, intent, contexts, session):
    print("codigo_cupom")

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


# Intent 2.5FinalizaPedido
def finaliza_pedido(query_text, payload, parameters, intent, contexts, session):
    print("finaliza_pedido")

    ctxPedido = list(filter(lambda ctx: "/contexts/pedido" in ctx["name"], contexts))
    ctxItem = ctxPedido[0]["parameters"]["pedido"]["itens"]
    ctxCupom = ctxPedido[0]["parameters"]["pedido"]["cupom"]

    if len(ctxItem) > 0:
        total = [float(item["preco"]) for item in ctxItem]
        total = sum(total)

        resumoItem = "\n".join(["#{} - {} - R${}".format(str(item["codigo"]), str(item["desc"]), str(item["preco"]))
                      for item in ctxItem])

        if (len(ctxCupom) > 0):
            desconto = total * ctxCupom[0]["desconto"]
            total = total - desconto
            resumoCupom = "\n\nDesconto: R${:.2f}".format(desconto)

        else:
            resumoCupom = "\nDesconto: R$00.00\n"

        resumoTotal = "\nTotal: R$" + str(total)

        resumo = "Seu pedido até o momento:\n\n"
        resumo += resumoItem
        resumo += resumoCupom
        resumo += resumoTotal

        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [resumo]
                    },
                },
                {
                    "text": {
                        "text": [payload['ok_response']]
                    },
                },
                {
                    "text": {
                        "text": payload['ok_options']
                    },
                }
            ],
            "source": "webhookdata"
        }

    else:
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": ["Você não possui nenhum item no seu pedido."]
                    },
                },
                {
                    "text": {
                        "text": ["Escolha uma opção:"]
                    },
                },
                {
                    "text": {
                        "text": payload['options']
                    },
                }
            ],
            "outputContexts": [
                {
                    "name": "{}/contexts/menu-opcoes".format(session),
                    "lifespanCount": 3,
                    "parameters": {}
                },
                {
                    "name": "{}/contexts/finalizar-pedido".format(session),
                    "lifespanCount": 0,
                    "parameters": {}
                }
            ],
            "source": "webhookdata"
        }


# Intent 2.6CancelaPedido
def cancela_pedido(query_text, payload, parameters, intent, contexts, session):
    print("cancela_pedido")

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


if __name__ == "__main__":
    app.secret_key = 'ItIsASecret'
    app.debug = True
    app.run()
