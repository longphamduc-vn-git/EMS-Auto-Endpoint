import re
import random
from flask import Flask, Response, request

app = Flask(__name__)

# ==========================================
# MOCK DATA CHO STEP 1: DANH SÁCH (6 SẢN PHẨM)
# ==========================================
XML_RET_STOCK_STATUS = """<?xml version="1.0" encoding="UTF-8"?>
<Root xmlns="http://www.nexacroplatform.com/platform/dataset">
    <Parameters>
        <Parameter id="ErrorCode">0</Parameter>
        <Parameter id="ErrorMsg">SUCCESS</Parameter>
    </Parameters>
    <Dataset id="ds_output">
        <ColumnInfo>
            <Column id="itemName" type="STRING" size="256"/>
            <Column id="inventoryItemId" type="STRING" size="256"/>
            <Column id="itemStatus" type="STRING" size="256"/>
            <Column id="availableQuantity" type="INT" size="256"/>
            <Column id="maker" type="STRING" size="256"/>
        </ColumnInfo>
        <Rows>
            <Row>
                <Col id="itemName">OLED Panel 55 inch</Col>
                <Col id="inventoryItemId">INV-A1001</Col>
                <Col id="itemStatus">Sẵn sàng</Col>
                <Col id="availableQuantity">150</Col>
                <Col id="maker">LG Display</Col>
            </Row>
            <Row>
                <Col id="itemName">LCD Mainboard Ver 2.0</Col>
                <Col id="inventoryItemId">INV-B2005</Col>
                <Col id="itemStatus">Hết hàng</Col>
                <Col id="availableQuantity">0</Col>
                <Col id="maker">Samsung SEMCO</Col>
            </Row>
            <Row>
                <Col id="itemName">Flex Cable 24-pin</Col>
                <Col id="inventoryItemId">INV-C3010</Col>
                <Col id="itemStatus">준비됨</Col> <Col id="availableQuantity">5000</Col>
                <Col id="maker">Foxconn</Col>
            </Row>
            <Row>
                <Col id="itemName">Power Supply Unit 800W</Col>
                <Col id="inventoryItemId">INV-D4040</Col>
                <Col id="itemStatus">Ready</Col> <Col id="availableQuantity">12</Col>
                <Col id="maker">Delta</Col>
            </Row>
            <Row>
                <Col id="itemName">Touch Sensor Glass</Col>
                <Col id="inventoryItemId">INV-E5055</Col>
                <Col id="itemStatus">Đang nhập</Col>
                <Col id="availableQuantity">0</Col>
                <Col id="maker">Corning</Col>
            </Row>
            <Row>
                <Col id="itemName">Test Jig Controller</Col>
                <Col id="inventoryItemId">INV-F6060</Col>
                <Col id="itemStatus">Sẵn sàng</Col>
                <Col id="availableQuantity">3</Col>
                <Col id="maker">In-house</Col>
            </Row>
        </Rows>
    </Dataset>
</Root>
"""

# ==========================================
# MOCK DATABASE CHO STEP 2 (CHI TIẾT TỪNG MÃ)
# ==========================================
# Khi tool của bạn loop qua danh sách trên và gọi gọi API chi tiết,
# Server sẽ dựa vào ID để trả về data tương ứng.
DETAIL_DATABASE = {
    "INV-A1001": {"desc": "Tấm nền OLED cong 55 inch cho Smart TV", "onhand": 160, "alloc": 10, "price": 450.00, "safety": 50},
    "INV-B2005": {"desc": "Bo mạch chủ điều khiển tín hiệu LCD", "onhand": 5, "alloc": 5, "price": 120.50, "safety": 20},
    "INV-C3010": {"desc": "Cáp đồng FFC 24 chân dài 15cm", "onhand": 5500, "alloc": 500, "price": 0.25, "safety": 1000},
    "INV-D4040": {"desc": "Bộ nguồn công nghiệp 800W chuẩn 80 Plus", "onhand": 12, "alloc": 0, "price": 85.00, "safety": 15},
    "INV-E5055": {"desc": "Kính cường lực tích hợp cảm ứng", "onhand": 0, "alloc": 0, "price": 15.75, "safety": 100},
    "INV-F6060": {"desc": "Bộ điều khiển Jig Test nội bộ", "onhand": 3, "alloc": 0, "price": 1200.00, "safety": 1},
}

# Template XML trả về cho Step 2
XML_DETAIL_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<Root xmlns="http://www.nexacroplatform.com/platform/dataset">
    <Parameters>
        <Parameter id="ErrorCode">0</Parameter>
        <Parameter id="ErrorMsg">SUCCESS</Parameter>
    </Parameters>
    <Dataset id="ds_output">
        <ColumnInfo>
            <Column id="inventoryItemId" type="STRING" size="256"/>
            <Column id="description" type="STRING" size="256"/>
            <Column id="onhandQuantity" type="INT" size="256"/>
            <Column id="allocatedQuantity" type="INT" size="256"/>
            <Column id="unitPricePo" type="FLOAT" size="256"/>
            <Column id="safetyStockQty" type="INT" size="256"/>
        </ColumnInfo>
        <Rows>
            <Row>
                <Col id="inventoryItemId">{item_id}</Col>
                <Col id="description">{desc}</Col>
                <Col id="onhandQuantity">{onhand}</Col>
                <Col id="allocatedQuantity">{alloc}</Col>
                <Col id="unitPricePo">{price}</Col>
                <Col id="safetyStockQty">{safety}</Col>
            </Row>
        </Rows>
    </Dataset>
</Root>
"""

@app.route('/emsspareparts/sp101/sp110Nav/RetStockStatusList.lgdn', methods=['POST'])
def mock_ret_stock_status():
    print("🚀 [STEP 1] Nhận Request lấy danh sách sản phẩm...")
    return Response(XML_RET_STOCK_STATUS, mimetype='application/xml')

@app.route('/emsspareparts/sp102/sp135Nav/retrieveItemInfoDetail.lgdn', methods=['POST'])
def mock_item_detail():
    # 1. Đọc payload XML do Tool automation của bạn gửi lên
    xml_data = request.data.decode('utf-8')
    
    # 2. Dùng Regex để tìm <Col id="inventoryItemId">MÃ_SẢN_PHẨM</Col>
    # Điều này giả định Tool của bạn build XML Request đúng chuẩn
    match = re.search(r'<Col id="inventoryItemId">(.*?)</Col>', xml_data)
    
    req_item_id = match.group(1) if match else "UNKNOWN_ID"
    print(f"🔄 [STEP 2] Nhận Request lấy chi tiết cho mã: {req_item_id}")

    # 3. Lấy data từ Database ảo, nếu không có thì trả về data rác (Mock random)
    if req_item_id in DETAIL_DATABASE:
        data = DETAIL_DATABASE[req_item_id]
    else:
        # Giả lập cho trường hợp Tool gửi lên ID linh tinh
        data = {
            "desc": f"Sản phẩm ảo {req_item_id}",
            "onhand": random.randint(0, 100),
            "alloc": random.randint(0, 10),
            "price": round(random.uniform(10.0, 500.0), 2),
            "safety": 10
        }

    # 4. Nhúng data vào Template XML và trả về
    response_xml = XML_DETAIL_TEMPLATE.format(
        item_id=req_item_id,
        desc=data["desc"],
        onhand=data["onhand"],
        alloc=data["alloc"],
        price=data["price"],
        safety=data["safety"]
    )
    
    return Response(response_xml, mimetype='application/xml')

if __name__ == '__main__':
    print("=====================================================")
    print("🏢 LGD EMS Mock Server V2 (Có hỗ trợ xử lý Loop data)")
    print("📡 Đang lắng nghe tại: http://localhost:9000")
    print("=====================================================")
    app.run(host='0.0.0.0', port=9000, debug=True)