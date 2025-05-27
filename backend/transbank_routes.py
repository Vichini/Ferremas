from flask import Blueprint, request, jsonify
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType

transbank_bp = Blueprint('transbank_bp', __name__)

@transbank_bp.route('/transbank/iniciar_pago', methods=['POST'])
def iniciar_pago():
    datos = request.get_json()
    monto = datos.get('monto')
    pedido_id = datos.get('pedido_id')

    if not monto or not pedido_id:
        return jsonify({"mensaje": "Monto y pedido_id son requeridos"}), 400

    try:
       
        transaction = Transaction(
            commerce_code="597055555532",
            api_key="597055555532",
            integration_type=IntegrationType.TEST
        )
        response = transaction.create(
            buy_order=str(pedido_id),
            session_id="session123",
            amount=monto,
            return_url="http://localhost:5000/transbank/confirmar_pago"
        )
        return jsonify({
            "url": response["url"],
            "token": response["token"]
        })
    except Exception as e:
        return jsonify({"mensaje": "Error al iniciar transacción", "error": str(e)}), 500

@transbank_bp.route('/transbank/confirmar_pago', methods=['POST'])
def confirmar_pago():
    token_ws = request.form.get("token_ws")

    if not token_ws:
        return jsonify({"mensaje": "Token no proporcionado"}), 400

    try:
        
        transaction = Transaction(
            commerce_code="597055555532",
            api_key="597055555532",
            integration_type=IntegrationType.TEST
        )
        response = transaction.commit(token_ws)
        return jsonify({
            "estado": response["status"],
            "monto": response["amount"],
            "orden_compra": response["buy_order"],
            "codigo_autorizacion": response["authorization_code"]
        })
    except Exception as e:
        return jsonify({"mensaje": "Error al confirmar transacción", "error": str(e)}), 500
