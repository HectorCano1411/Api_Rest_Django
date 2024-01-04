# utils.py

def calcular_nuevo_saldo_contable(transferencia):
    # Supongamos que transferencia tiene un campo 'monto' que representa el monto de la transferencia
    monto_transferencia = transferencia.monto

    # Lógica específica para calcular el nuevo saldo
    # En este ejemplo, simplemente se suma el monto de la transferencia al saldo actual
    nuevo_saldo = transferencia.nuevo_registro.saldo_contable + monto_transferencia

    return nuevo_saldo
