from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

TABLO_DIZIN = os.path.join(os.path.dirname(__file__), '..', 'data', 'tablolar')
os.makedirs(TABLO_DIZIN, exist_ok=True)

def tablo_yolu(tablo_adi):
    return os.path.join(TABLO_DIZIN, f"{tablo_adi}.jxt")

def tablo_oku(tablo_adi):
    yol = tablo_yolu(tablo_adi)
    if not os.path.exists(yol):
        return None
    with open(yol, 'r', encoding='utf-8') as f:
        return json.load(f)

def tablo_yaz(tablo_adi, veri):
    yol = tablo_yolu(tablo_adi)
    with open(yol, 'w', encoding='utf-8') as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

@app.route('/olustur', methods=['POST'])
def olustur():
    veri = request.json
    tablo_adi = veri.get('tablo')
    sutunlar = veri.get('sutunlar')
    if not tablo_adi or not sutunlar:
        return jsonify({'hata': 'tablo ve sutunlar gerekli'}), 400
    if os.path.exists(tablo_yolu(tablo_adi)):
        return jsonify({'hata': 'tablo zaten var'}), 400
    tablo_yaz(tablo_adi, {'sutunlar': sutunlar, 'satirlar': []})
    return jsonify({'mesaj': f'{tablo_adi} tablosu oluşturuldu'})

@app.route('/ekle', methods=['POST'])
def ekle():
    veri = request.json
    tablo_adi = veri.get('tablo')
    satir = veri.get('satir')
    tablo = tablo_oku(tablo_adi)
    if tablo is None:
        return jsonify({'hata': 'tablo bulunamadı'}), 404
    tablo['satirlar'].append(satir)
    tablo_yaz(tablo_adi, tablo)
    return jsonify({'mesaj': 'satır eklendi'})

@app.route('/al', methods=['GET'])
def al():
    tablo_adi = request.args.get('tablo')
    sart_sutun = request.args.get('sart_sutun')
    sart_deger = request.args.get('sart_deger')
    tablo = tablo_oku(tablo_adi)
    if tablo is None:
        return jsonify({'hata': 'tablo bulunamadı'}), 404
    satirlar = tablo['satirlar']
    if sart_sutun and sart_deger:
        satirlar = [s for s in satirlar if str(s.get(sart_sutun)) == sart_deger]
    return jsonify({'satirlar': satirlar})

@app.route('/sil', methods=['DELETE'])
def sil():
    veri = request.json
    tablo_adi = veri.get('tablo')
    sart_sutun = veri.get('sart_sutun')
    sart_deger = veri.get('sart_deger')
    tablo = tablo_oku(tablo_adi)
    if tablo is None:
        return jsonify({'hata': 'tablo bulunamadı'}), 404
    tablo['satirlar'] = [s for s in tablo['satirlar'] if str(s.get(sart_sutun)) != str(sart_deger)]
    tablo_yaz(tablo_adi, tablo)
    return jsonify({'mesaj': 'satır silindi'})

@app.route('/guncelle', methods=['PUT'])
def guncelle():
    veri = request.json
    tablo_adi = veri.get('tablo')
    sart_sutun = veri.get('sart_sutun')
    sart_deger = veri.get('sart_deger')
    yeni = veri.get('yeni')
    tablo = tablo_oku(tablo_adi)
    if tablo is None:
        return jsonify({'hata': 'tablo bulunamadı'}), 404
    for satir in tablo['satirlar']:
        if str(satir.get(sart_sutun)) == str(sart_deger):
            satir.update(yeni)
    tablo_yaz(tablo_adi, tablo)
    return jsonify({'mesaj': 'satır güncellendi'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
