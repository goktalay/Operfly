from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
F="Arial"
T="Tahmin"; D="Distribütör fiyatı"; B="Belirsiz (parça seçilmedi)"
K="Kart"; M="Modül"; S="Seçildi"; O="Öneri"; A="Açık"; TS="Tasarımda netleşir"
ST="STMicroelectronics"; TI="Texas Instruments"; HW="Harwin"
# ad, fiyat, dayanak, not, üretici, parça/seri, tür, durum
prices=[
("Ana işlemci",22,T,"",ST,"STM32H753IIK6",K,S),
("IO/failsafe işlemcisi",8,T,"Ana işlemciden bağımsız; CAN FD ile omurgaya doğrudan bağlı. Core şematiğinde seçildi",ST,"STM32G0B1CET6",K,S),
("Düğüm işlemcisi",8,T,"İki CAN FD hattı olan küçük işlemci; ortak düğüm devresinde seçildi",ST,"STM32G0B1CET6",K,S),
("Güvenli eleman",4,T,"P-384 anahtar desteği gerekir; şematiklerde SE050E2HQ1 yazıldı, alt tür teyit edilecek",  "NXP","EdgeLock SE050 (SE050E2HQ1)",K,S),
("IMU 1",8,T,"","TDK InvenSense","ICM-42688-P",K,S),
("IMU 2",8,T,"","Bosch","BMI088",K,S),
("IMU 3",8,T,"","TDK InvenSense","ICM-45686",K,S),
("Barometre",5,T,"İki farklı tip. ICP-20100 dağıtıcıda yeni tasarım için önerilmediğinden MS5611 seçildi; fiyat teyit edilecek","Bosch / TE Connectivity","BMP390 ve MS5611-01BA03",K,S),
("Pusula",2,T,"","iSentek","IST8310",K,S),
("FRAM bellek",8,T,"1 Mbit, SOIC-8","Infineon","FM25V10-G",K,S),
("CAN FD alıcı-verici",2,T,"Core şematiğinde TJA1051TK/3; TCAN1044 pin uyumlu seçenek","NXP / "+TI,"TJA1051TK/3",K,S),
("Gigabit Ethernet PHY",4,T,"",TI,"DP83867 serisi",K,O),
("10/100 Ethernet PHY (RMII)",2,T,"Core için; işlemcinin Ethernet arayüzü en çok 100 Mbit","Microchip","LAN8742A-CZ",K,S),
("Ethernet trafosu (10/100)",3,T,"Core ve Radio; 100 Mbit çalışan kartlarda omurga ile yalıtım","Bourns","PT61017PEL",K,S),
("Radyo modülü soğutucusu ve ısı dolgusu",8,T,"Modül yaklaşık 7,5 W ısı üretir; üretici 25 x 25 mm soğutucu ve ısı dolgusu ister. Kasa tasarımında netleşir","Wakefield-Vette / Laird","625-25ABT4E, Tflex HR600",K,TS),
("microSD yuvası",2,T,"Core: uçuş kaydı. Nav: ham ölçüm kaydı. Endüstriyel microSD kart ayrıca alınır","Hirose","DM3AT-SF-PEJM5",K,S),
("Peltier modülü ve sürücüsü",25,T,"","","",K,A),
("Watchdog, gözetleyiciler, enerji deposu",20,T,"","","",K,TS),
("Kart içi regülatörler",15,T,"Düğüm: AP63205 + LP5907; Hub ve PC adaptöründe ayrıca TPS62130; Nav'da 3,3 V için AP7361C (1 A); RX ve Radio'da radyo modülü için AP63201; Radio'da 3,3 V için AP63203","Diodes / "+TI,"AP63205QWU, LP5907MFX-3.3, TPS62130, AP7361C-33E, AP63201WU, AP63203QWU",K,S),
("Pasifler, kristal, ESD, küçük malzeme",25,T,"0402 kılıf","","",K,TS),
("Operfly Bus prizi, 20 kontak",17,D,"RS tek adet 13,69 £, 5+ adet 12,29 £. Kaynak: uk.rs-online.com/web/p/pcb-sockets/2871000",HW,"Gecko-SL (G125), 20 kontak",K,S),
("Operfly Bus fişi + kısa kablo",45,T,"Hazır kablo takımı için kaba tahmin",HW,"Gecko-SL (G125), 20 kontak",K,S),
("Motor/servo çıkış konnektörü, 26 kontak",22,T,"",HW,"Gecko-SL (G125), 26 kontak",K,S),
("SMA konnektör",5,T,"","","",K,TS),
("Batarya giriş konnektörü (yüksek akım)",15,T,"Power şematiğinde XT60; fiyat teyit edilecek","Amass","XT60",K,S),
("PCB, 8 katman Sınıf 3 (küçük kart)",90,T,"10 adetlik seride kart başına; kurulum bedeli dahil","","",K,TS),
("PCB, 8 katman Sınıf 3 (büyük kart)",180,T,"10 adetlik seride kart başına; kurulum bedeli dahil","","",K,TS),
("Dizgi, X-ray, konformal kaplama",200,T,"10 adetlik seride kart başına","","",K,TS),
("Gigabit anahtar entegresi seti (12 port, PTP)",120,B,"Hub şematiğinde 3 anahtar + 12 trafo + 3 regülatör; fiyat teyit edilecek","Microchip / HALO","3 x KSZ9567RTXI, 12 x TG111-MSC13LF",K,S),
("Port koruması: elektronik sigorta + akım ölçümü",6,T,"Port başına; ortak: 2 x PCA9555, 1 x CD74HC4067",TI,"TPS26630RGER",K,S),
("Geniş girişli güç katı, 150 W, çift giriş",90,T,"6–60 V giriş; denetleyici, 2 ideal diyot, giriş ölçümü. MOSFET ve bobin seçimi doğrulanacak; fiyat teyit edilecek","Analog Devices / "+TI,"LT8705A, 2 x LTC4359, INA228",K,S),
("Servo güç rayı (yedekli)",45,T,"İki bağımsız 5 A regülatör + 2 ideal diyot; fiyat teyit edilecek",TI+" / Analog Devices","2 x TPS54560B, 2 x LTC4359",K,S),
("Temassız akım algılayıcı, 400 A",35,T,"","","",K,A),
("Jetson taşıyıcı devresi (soket, güç, soğutma)",70,T,"Vision şematiği: 260 uçlu soket, M.2 soketi, 2 x 3,3 V regülatör, 1,8 V, seviye çevirici, giriş MOSFET'i, fan ve USB; soğutucu kasa tasarımında","TE / "+TI+" / Vishay","SO-DIMM 260 soket, 2 x TPS62130, TXS0104E, SUD50P04-08",K,TS),
("PCIe gigabit Ethernet denetleyici",8,T,"Vision: kamera portu başına bir adet, ayar belleğiyle; fiyat teyit edilecek","Intel / Winbond","WGI210IT, W25Q16JV",K,S),
("Gigabit Ethernet trafosu",4,T,"Vision: omurga portu ve iki kamera portu; fiyat teyit edilecek","HALO","TG111-MSC13LF",K,S),
("GNSS RF ön ucu (LNA, filtre, anten beslemesi)",30,T,"Nav şematiği: alıcı anten beslemesini ve korumasını içinde taşır; kartta yalnızca anten regülatörü ve çift anten seçeneğinin elemanları var. Tahmin şematikten yüksek kaldı, fiyat teyidinde düşürülecek",TI+" / Würth","LP5907MFX-3.3, 744786139A, SESD0402X1BN",K,S),
("SIM yuvası, eSIM, anten bağlantıları",20,T,"Cell şematiği: M.2 Key B soketi, 2 x nano-SIM yuvası ve koruma dizisi, USB anahtarı; 4 anten kablosu (modül konnektöründen SMA'ya). Lehimli eSIM sonraki revizyonda","TE / GCT / "+TI+" / onsemi","2199119-x, SIM8060-6-0-14-00, TPD4E05U06, FSUSB42",K,S),
("PCIe gigabit Ethernet denetleyici (Cell)",3,T,"Cell şematiği: modem PCIe kök kipinde bu entegreyi sürer; fiyat teyit edilecek","Realtek","RTL8111H-CG",K,S),
("Modem besleme regülatörü (3,8 V, 5 A)",12,T,"Cell şematiği: regülatör, bobin, diyot, 2 x 220 uF polimer kondansatör; fiyat teyit edilecek",TI+" / Coilcraft","TPS54560BDDAR, XAL7070-103",K,S),
("Fark basınç sensörü",40,T,"Air şematiği: ±1 psi, 24 bit, çift hortum uçlu; fiyat teyit edilecek. Pitot ısıtıcı anahtarı (NCV8402) küçük malzemede","TE Connectivity","5525DSO-DB001DS",K,S),
("Yalıtımlı motor girişleri (devir, sıcaklık, yakıt)",35,T,"Engine şematiği: yalıtımlı besleme modülü, sayısal yalıtıcı, 8 kanallı çevirici, 2 termokupl yükselteci, 3 optokuplör, ateşleme anahtarı (2 x DMP3099L); fiyat teyit edilecek","Murata / "+TI+" / Microchip / Analog Devices / Lite-On","NXE1S0505MC, ISO7762DW, MCP3208, 2 x AD8495, 3 x LTV-817S",K,S),
("Hall etkili gimbal",60,T,"Model seçilmedi. Aday sınıf: 3,3 V analog çıkışlı Hall gimbal (ör. RadioMaster AG01). Ürün sayfalarında uç sırası yok; kablo numune üzerinde uyarlanır","","",K,A),
("Anahtar, tekerlek ve düğme seti",40,T,"6 anahtar, 2 tekerlek, 2 düğme, 5 yönlü tuş; kasa tasarımıyla seçilecek. Giriş kartına JST-GH kabloyla bağlanır","","",K,A),
("Küçük ekran (Pilot T)",30,T,"Pilot T şematiği: 128 x 64 yarı geçirgen LCD + kehribar arka ışık; karta elle lehimlenir. Fiyat teyit edilecek","Display Visions","EA DOGM128W-6, EA LED55X46-A",K,S),
("Kumanda bataryası ve şarj devresi",70,T,"Pilot 12 şematiği: tek hücreli (1S) korumalı, NTC'li Li-ion paket (seçilmedi; öneri 5000 mAh ve üzeri) + şarj/güç yolu, batarya ölçer, 3,3 V ve radyo beslemesi",TI,"BQ24075RGT, BQ27441DRZR-G1A, TPS63001, TPS61230, LMV393",K,TS),
("Pilot Pro bataryası ve şarj devresi",150,T,"Pilot Pro şematiği (1. adım): 4 hücreli akıllı Li-ion paket (seçilmedi; 100 Wh altı önerilir) + şarj/güç yolu, USB-C güç anlaşması, giriş anahtarları, batarya anahtarı. Fiyat teyit edilecek",TI+" / "+ST+" / Vishay","BQ25798RQMR, STUSB4500QTR, 2 x SUD50P04-08",K,O),
("USB–Gigabit Ethernet köprüsü",10,T,"Köprü + USB göbeği + trafo; fiyat teyit edilecek","Microchip / HALO","LAN7500i, USB2514B, TG111-MSC13LF",K,S),
("USB Type-C konnektör",6,T,"","","",K,TS),
("USB göbeği ve dış USB portu",8,T,"Pilot Pro şematiği: 4 portlu göbek, 2 güç anahtarı, USB-A konnektör, korumalar; fiyat teyit edilecek","Microchip / "+TI+" / Molex","USB2514Bi-AEZG, 2 x TPS2051CDBV, 67643",K,S),
("Anten takip motorları ve sürücüleri (2 eksen)",250,T,"","","",K,A),
("GNSS modülü",520,D,"DigiKey tek adet 472 € / 424 £. Kaynak: digikey.es/en/products/detail/septentrio-inc/410322/12503897","Septentrio","mosaic-X5",M,S),
("Geniş bant radyo modülü (2,4 GHz, 1 W)",450,D,"ModalAI tek adet 449,99 $. Kaynak: modalai.com/products/oem-m0048-4-1","Microhard","pMDDL2450",M,S),
("Kumanda radyo modülü (frekans atlamalı, 1 W)",86,D,"Karta lehimlenen sürüm; satıcıda tek adet 86 $. Kaynak: irlock.com/products/rfd900ux-smt-modem. 868 MHz sürümü (RFD868ux-SMT) aynı ayak izine oturur; fiyatı teyit edilecek","RFDesign","RFD900ux-SMT",M,S),
("Jetson modülü",800,D,"Arrow liste fiyatı 699 $ (stok yok, 24 hafta); Avrupa distribütörlerinde 750–818 €. Kaynak: arrow.com/en/products/900-13767-0000-000/nvidia","NVIDIA","Jetson Orin NX 16 GB (900-13767-0000-000)",M,S),
("M.2 NVMe 256 GB (endüstriyel)",60,T,"","","",M,A),
("10 inç gün ışığında okunur dokunmatik ekran",400,T,"","","",M,A),
("CRPA modülü, 4 kanal, L1",1342,D,"Satıcı sayfası tek adet 1.342 $ (sayfa verisinde 1.342–1.492 aralığı). Kaynak: yundingantenna.com (YDAJ-P4065). Performans üretici beyanı; ithalat koşulları teyit edilecek","Yunding Antenna","YDAJ-P4065",M,S),
("5G M.2 modem",250,B,"Aday: Quectel RM520N-GL (M.2 Key B, 30 x 52 mm; n28 ve n78 dahil). Avrupa satıcısında KDV dahil 289 EUR (cartft.com); cihaz kaydı ve operatör uyumluluğu teyit edilecek","Quectel","RM520N-GL",M,O),
("Mesafe sensörü çekirdeği, 10 m",50,T,"Aday: 12 m, 5 V, seri port/I2C; numuneyle kesinleşecek; fiyat teyit edilecek","Benewake","TFmini Plus",M,O),
("Mesafe sensörü çekirdeği, 30 m",150,T,"Aday: 40 m (%10 yansıtmada 13,5 m), 5 V, seri port/I2C; fiyat teyit edilecek","Benewake","TF02-Pro",M,O),
("Mesafe sensörü çekirdeği, 100 m",260,D,"Aday: 100 m, IP67; 5 V seri port sürümü alınmalı. Satıcılarda tek adet 205 € ile 259 $ arası. Kaynak: exp-tech.de/en/products/tf03-100uart-can, worldronemarket.com/product/benewake-tf03-100-lidar-module","Benewake","TF03-100 (UART/CAN, 5 V)",M,O),
]
PR={p[0]:p for p in prices}
small="PCB, 8 katman Sınıf 3 (küçük kart)"; big="PCB, 8 katman Sınıf 3 (büyük kart)"
asm="Dizgi, X-ray, konformal kaplama"; pas="Pasifler, kristal, ESD, küçük malzeme"
node=[("Düğüm işlemcisi",1),("Güvenli eleman",1),("CAN FD alıcı-verici",2)]
bus="Operfly Bus prizi, 20 kontak"; reg="Kart içi regülatörler"; sma="SMA konnektör"; phy="Gigabit Ethernet PHY"
WB="Geniş bant radyo modülü (2,4 GHz, 1 W)"; KR="Kumanda radyo modülü (frekans atlamalı, 1 W)"
GK=[("Hall etkili gimbal",2),("Anahtar, tekerlek ve düğme seti",1),("Düğüm işlemcisi",1),(pas,1),(small,1),(asm,1)]  # kumanda giriş kartı (ikinci kart)
def merge(items):
    d={}
    for n,q in items: d[n]=d.get(n,0)+q
    return list(d.items())
P=[
("Operfly Core","OPFCOR",1,[("Ana işlemci",1),("IO/failsafe işlemcisi",1),("Güvenli eleman",1),("IMU 1",1),("IMU 2",1),("IMU 3",1),("Barometre",2),("Pusula",1),("FRAM bellek",1),("CAN FD alıcı-verici",2),("10/100 Ethernet PHY (RMII)",1),("Ethernet trafosu (10/100)",1),("microSD yuvası",1),("Peltier modülü ve sürücüsü",1),("Watchdog, gözetleyiciler, enerji deposu",1),(reg,1),(pas,1),(bus,2),("Motor/servo çıkış konnektörü, 26 kontak",1),(small,1),(asm,1)]),
("Operfly Hub","OPFHUB",1,[("Gigabit anahtar entegresi seti (12 port, PTP)",1)]+node+[("Port koruması: elektronik sigorta + akım ölçümü",12),(reg,1),(pas,2),(bus,12),(big,1),(asm,1)]),
("Operfly Power","OPFPWR",1,[("Geniş girişli güç katı, 150 W, çift giriş",1),("Servo güç rayı (yedekli)",1),("Temassız akım algılayıcı, 400 A",1)]+node+[("Batarya giriş konnektörü (yüksek akım)",2),(pas,1),(bus,1),(small,1),(asm,1)]),
("Operfly PC adaptörü","OPFPCA",1,[("USB–Gigabit Ethernet köprüsü",1)]+node+[("USB Type-C konnektör",1),(pas,1),("Operfly Bus fişi + kısa kablo",1),(small,1),(asm,1)]),
("Operfly Nav","OPFNAV",2,[("GNSS modülü",1),("GNSS RF ön ucu (LNA, filtre, anten beslemesi)",1)]+node+[("Pusula",1),("microSD yuvası",1),("USB Type-C konnektör",1),(reg,1),(pas,1),(sma,2),(bus,1),(small,1),(asm,1)]),
("Operfly Radio","OPFRAD",2,[(WB,1)]+node+[("Ethernet trafosu (10/100)",1),("Radyo modülü soğutucusu ve ısı dolgusu",1),(reg,1),(pas,1),(sma,2),(bus,1),(small,1),(asm,1)]),
("Operfly RX","OPFRCV",2,[(KR,1)]+node+[(reg,1),(pas,1),(sma,2),(bus,1),(small,1),(asm,1)]),
("Operfly Pilot 12","OPFK12",2,merge([(KR,1),("Güvenli eleman",1),("Kumanda bataryası ve şarj devresi",1),(sma,2),(pas,1),(small,1),(asm,1)]+GK)),
("Operfly Air","OPFAIR",2,[("Fark basınç sensörü",1),("Barometre",1)]+node+[(pas,1),(bus,1),(small,1),(asm,1)]),
("Operfly Engine","OPFENG",2,[("Yalıtımlı motor girişleri (devir, sıcaklık, yakıt)",1)]+node+[(pas,1),(bus,1),(small,1),(asm,1)]),
("Operfly Vision","OPFVIS",3,[("Jetson modülü",1),("M.2 NVMe 256 GB (endüstriyel)",1),("Jetson taşıyıcı devresi (soket, güç, soğutma)",1),("IMU 1",1),("PCIe gigabit Ethernet denetleyici",2),("Gigabit Ethernet trafosu",3),("Port koruması: elektronik sigorta + akım ölçümü",3)]+node+[(reg,1),(pas,1),(bus,3),(big,1),(asm,1)]),
("Operfly Range 10","OPFR10",3,[("Mesafe sensörü çekirdeği, 10 m",1)]+node+[(pas,1),(bus,1),(small,1),(asm,1)]),
("Operfly Range 30","OPFR30",3,[("Mesafe sensörü çekirdeği, 30 m",1)]+node+[(pas,1),(bus,1),(small,1),(asm,1)]),
("Operfly Range 100","OPFR1H",3,[("Mesafe sensörü çekirdeği, 100 m",1)]+node+[(pas,1),(bus,1),(small,1),(asm,1)]),
("Operfly Cell","OPFCEL",4,[("5G M.2 modem",1),("SIM yuvası, eSIM, anten bağlantıları",1),("PCIe gigabit Ethernet denetleyici (Cell)",1),("Gigabit Ethernet trafosu",1),("Modem besleme regülatörü (3,8 V, 5 A)",1),("Radyo modülü soğutucusu ve ısı dolgusu",1),("USB Type-C konnektör",1)]+node+[(reg,1),(pas,1),(sma,4),(bus,1),(small,1),(asm,1)]),
("Operfly Pilot T","OPFKTL",4,merge([(KR,1),("Güvenli eleman",1),("Küçük ekran (Pilot T)",1),("Kumanda bataryası ve şarj devresi",1),(sma,2),(pas,1),(small,1),(asm,1)]+GK)),
("Operfly Pilot Pro","OPFKPR",4,merge([("Jetson modülü",1),(WB,1),(KR,1),("10 inç gün ışığında okunur dokunmatik ekran",1),("M.2 NVMe 256 GB (endüstriyel)",1),("Jetson taşıyıcı devresi (soket, güç, soğutma)",1),("Güvenli eleman",1),("Pilot Pro bataryası ve şarj devresi",1),("CAN FD alıcı-verici",2),("Düğüm işlemcisi",1),("Güvenli eleman",1),("Gigabit Ethernet trafosu",2),("PCIe gigabit Ethernet denetleyici",1),("Ethernet trafosu (10/100)",1),("Radyo modülü soğutucusu ve ısı dolgusu",1),("Port koruması: elektronik sigorta + akım ölçümü",1),("USB göbeği ve dış USB portu",1),(reg,1),(sma,4),(pas,1),(bus,1),(big,1),(asm,1)]+GK)),
("Operfly Base","OPFBAS",4,[("GNSS modülü",1),("GNSS RF ön ucu (LNA, filtre, anten beslemesi)",1)]+node+[("microSD yuvası",1),("USB Type-C konnektör",1),(reg,1),(pas,1),(sma,2),(bus,1),(small,1),(asm,1)]),
("Operfly Ground Radio","OPFGRD",4,[(WB,1),(KR,1)]+node+[(phy,1),(reg,1),(pas,1),(sma,4),(bus,2),(big,1),(asm,1)]),
("Operfly Tracker","OPFTRK",4,[("Anten takip motorları ve sürücüleri (2 eksen)",1)]+node+[(reg,1),(pas,1),(bus,1),(small,1),(asm,1)]),
("Operfly Shield","OPFSHD",4,[("CRPA modülü, 4 kanal, L1",1)]+node+[(reg,1),(pas,1),(sma,2),(bus,1),(small,1),(asm,1)]),
]
for n,c,s,its in P:
    for i,q in its: assert i in PR,(n,i)
wb=Workbook()
hf=Font(name=F,bold=True,color="FFFFFF"); hfill=PatternFill("solid",fgColor="1F3A34")
inp=Font(name=F,color="0000FF"); nf=Font(name=F); bf=Font(name=F,bold=True); gf=Font(name=F,color="008000"); sf=Font(name=F,color="555555")
yel=PatternFill("solid",fgColor="FFFF00"); band=PatternFill("solid",fgColor="EEF3F1"); thin=Side(style="thin",color="BBBBBB")
USD='$#,##0;($#,##0);-'
def head(ws,cols,widths):
    for i,(c,w) in enumerate(zip(cols,widths),1):
        x=ws.cell(row=1,column=i,value=c); x.font=hf; x.fill=hfill; x.alignment=Alignment(wrap_text=True,vertical="center")
        ws.column_dimensions[get_column_letter(i)].width=w
    ws.row_dimensions[1].height=32; ws.freeze_panes="A2"
so=wb.active; so.title="Ozet"
sb=wb.create_sheet("BOM"); sa=wb.create_sheet("Satin_Alma"); sp=wb.create_sheet("Fiyatlar"); sv=wb.create_sheet("Aciklamalar")
# Fiyatlar
head(sp,["Kalem","Birim fiyat ($)","Fiyat dayanağı","Üretici","Parça / seri","Tür","Seçim durumu","Not / kaynak"],[50,14,26,22,40,9,20,80])
for r,(n,p,k,note,mf,pn,tur,dur) in enumerate(prices,2):
    sp.cell(row=r,column=1,value=n).font=nf
    c=sp.cell(row=r,column=2,value=p); c.font=inp; c.number_format='$#,##0'
    for col,v in ((3,k),(4,mf),(5,pn),(6,tur),(7,dur)): sp.cell(row=r,column=col,value=v).font=nf
    x=sp.cell(row=r,column=8,value=note); x.font=nf; x.alignment=Alignment(wrap_text=True)
    if dur==A: sp.cell(row=r,column=7).fill=yel
    if k==B: c.fill=yel
LP=len(prices)+1
sp.auto_filter.ref="A1:H%d"%LP
# BOM
head(sb,["Ürün","Kod","Kalem","Üretici","Parça / seri","Tür","Seçim durumu","Adet","Birim fiyat ($)","Tutar ($)"],[24,9,48,20,38,8,19,7,13,12])
r=2
for name,code,stage,items in P:
    items=sorted(items,key=lambda x:(PR[x[0]][6]!=M,[p[0] for p in prices].index(x[0])))
    for it,q in items:
        _,_,_,_,mf,pn,tur,dur=PR[it]
        for col,v in ((1,name),(2,code),(3,it),(4,mf),(5,pn),(6,tur),(7,dur)): sb.cell(row=r,column=col,value=v).font=nf
        if dur==A: sb.cell(row=r,column=7).fill=yel
        sb.cell(row=r,column=8,value=q).font=inp
        d=sb.cell(row=r,column=9,value='=INDEX(Fiyatlar!$B$2:$B$%d,MATCH(C%d,Fiyatlar!$A$2:$A$%d,0))'%(LP,r,LP)); d.font=gf; d.number_format='$#,##0'
        e=sb.cell(row=r,column=10,value='=H%d*I%d'%(r,r)); e.font=nf; e.number_format='$#,##0'
        r+=1
LB=r-1
sb.auto_filter.ref="A1:J%d"%LB
rng=lambda col:"BOM!$%s$2:$%s$%d"%(col,col,LB)
# Özet (ağaç)
head(so,["Donanım / altındaki hazır modül","Kod","Tasarım aşaması","Kart üretim maliyeti ($)","Hazır modüller ($)","Toplam ($)","Parçası seçilmemiş kalem payı ($)"],[50,10,10,18,16,14,22])
r=2; prodrows=[]
for name,code,stage,items in P:
    pr=r; prodrows.append(r)
    so.cell(row=r,column=1,value=name).font=bf; so.cell(row=r,column=2,value=code).font=bf; so.cell(row=r,column=3,value=stage).font=bf
    cells={4:'=SUMIFS(%s,%s,A%d,%s,"Kart")'%(rng("J"),rng("A"),r,rng("F")),
           5:'=SUMIFS(%s,%s,A%d,%s,"Modül")'%(rng("J"),rng("A"),r,rng("F")),
           6:'=D%d+E%d'%(r,r),
           7:'=SUMIFS(%s,%s,A%d,%s,"Açık")'%(rng("J"),rng("A"),r,rng("G"))}
    for col,f in cells.items():
        c=so.cell(row=r,column=col,value=f); c.font=Font(name=F,bold=True,color="000000" if col==6 else "008000"); c.number_format=USD
    for col in range(1,8): so.cell(row=r,column=col).fill=band
    r+=1
    for it,q in items:
        if PR[it][6]==M:
            lab="    └ %s%s"%(("%d × "%q) if q>1 else "", it)+(" — %s %s"%(PR[it][4],PR[it][5]) if PR[it][5] else "")
            so.cell(row=r,column=1,value=lab).font=sf
            c=so.cell(row=r,column=5,value='=SUMIFS(%s,%s,A%d,%s,"%s")'%(rng("J"),rng("A"),pr,rng("C"),it)); c.font=Font(name=F,color="008000"); c.number_format=USD
            r+=1
tr=r
so.cell(row=tr,column=1,value="TOPLAM (her donanımdan birer adet, %d ürün)"%len(P)).font=bf
for col in "DEFG":
    c=so["%s%d"%(col,tr)]; c.value="="+"+".join("%s%d"%(col,x) for x in prodrows); c.font=bf; c.number_format='$#,##0'; c.border=Border(top=thin)
so.cell(row=tr+2,column=1,value="Yeşil: BOM sayfasından gelir · Sarı: parçası henüz seçilmemiş · Fiyat değiştirmek için Fiyatlar sayfasındaki mavi hücreleri düzenleyin.").font=Font(name=F,size=9)
# Satın alma
head(sa,["Kalem","Üretici","Parça / seri","Tür","Seçim durumu","Toplam adet (her donanımdan 1)","Birim fiyat ($)","Tutar ($)","Kullanıldığı donanım sayısı"],[50,22,40,9,20,16,14,13,16])
for r,(n,p,k,note,mf,pn,tur,dur) in enumerate(prices,2):
    for col,v in ((1,n),(2,mf),(3,pn),(4,tur),(5,dur)): sa.cell(row=r,column=col,value=v).font=nf
    if dur==A: sa.cell(row=r,column=5).fill=yel
    sa.cell(row=r,column=6,value='=SUMIFS(%s,%s,A%d)'%(rng("H"),rng("C"),r)).font=gf
    c=sa.cell(row=r,column=7,value='=Fiyatlar!B%d'%r); c.font=gf; c.number_format='$#,##0'
    c=sa.cell(row=r,column=8,value='=F%d*G%d'%(r,r)); c.font=nf; c.number_format='$#,##0'
    sa.cell(row=r,column=9,value='=COUNTIFS(%s,A%d)'%(rng("C"),r)).font=gf
sa.auto_filter.ref="A1:I%d"%LP
t=LP+1
sa.cell(row=t,column=1,value="TOPLAM").font=bf
c=sa.cell(row=t,column=8,value='=SUM(H2:H%d)'%LP); c.font=bf; c.number_format='$#,##0'; c.border=Border(top=thin)
sa.cell(row=t+1,column=1,value="Denetim: Özet toplamı ile fark (0 olmalı)").font=nf
c=sa.cell(row=t+1,column=8,value='=H%d-Ozet!F%d'%(t,tr)); c.font=nf; c.number_format='$#,##0;($#,##0);0'
# Açıklamalar
sv.column_dimensions["A"].width=125
lines=["Operfly malzeme listesi (BOM) — 14 Kasım 2026",
"Para birimi ABD doları. Fiyatların çoğu kaba mühendislik tahminidir; teklif alınmamıştır. 'Distribütör fiyatı' internetteki liste fiyatına dayanır; 'Belirsiz' parça henüz seçilmemiştir.",
"Sayfalar: Ozet = donanım başına maliyet, hazır modüller donanımın altında ağaç biçiminde. BOM = donanım başına kalem kalem liste. Satin_Alma = her donanımdan birer adet üretmek için toplam parça ihtiyacı. Fiyatlar = birim fiyatlar ve kaynaklar.",
"Seçim durumu: 'Seçildi' = şartnamede kararlaştırılan parça. 'Öneri' = Claude'un önerdiği parça ailesi; şematik aşamasında doğrulanacak, kullanıcı onayı beklenir. 'Açık' = parça henüz seçilmedi (sarı). 'Tasarımda netleşir' = şematik ve yerleşim sırasında belirlenecek genel kalem grubu.",
"Kart üretim maliyeti: PCB, dizgi ve kart üstü malzeme. Hazır modüller: GNSS modülü, radyo modülleri, Jetson, NVMe, ekran, 5G modem ve mesafe sensörü çekirdekleri; ayrı satın alınıp karta takılır.",
"PCB ve dizgi fiyatları 10 adetlik seriye göre kart başınadır (kurulum bedeli dahil); tek adet üretimde belirgin yükselir, 100+ adette düşer.",
"Kumandalarda (Pilot 12, Pilot T, Pilot Pro) iki kart vardır: ana kart ve ortak kumanda giriş kartı. İkisinin malzemesi aynı listede birleştirilmiştir; bu yüzden PCB ve dizgi adetleri 2'dir.",
"Operfly Shield sürüm 1: hazır 4 kanallı L1 CRPA modülü (Yunding Antenna YDAJ-P4065, 1.342 $) + Operfly arayüz kartı. Sürüm 2 (kendi 8 kanala hazır işlem kartımız) bu listede yoktur; kaba tahmini kart başına yaklaşık 1.000 $ idi.",
"RF tek standarttır: 12 km. Video ve telemetri geniş bant modül (2,4 GHz), kumanda ayrı bir frekans atlamalı modül üzerinden taşınır. Operfly Link ve ayrı radyo çekirdeği kartı kaldırılmıştır.",
"Konnektör: Harwin Gecko-SL (vida kilitli, 1,25 mm); sızdırmazlık kasa seviyesinde sağlanır.",
"Dahil olmayanlar: mekanik kasa ve soğutma parçaları, kartlar arası kablolar (PC adaptörü hariç), antenler, kameralar, bataryalar, motor ve ESC, yazılım geliştirme, tasarım ve prototip tekrarları, test ve sertifikasyon, gümrük, vergi ve nakliye.",
"Bir fiyatı değiştirmek için Fiyatlar sayfasındaki mavi hücreyi, adedi değiştirmek için BOM sayfasındaki mavi hücreyi düzenleyin; diğer sayfalar kendiliğinden güncellenir."]
for i,l in enumerate(lines,1):
    c=sv.cell(row=i,column=1,value=l); c.font=bf if i==1 else nf; c.alignment=Alignment(wrap_text=True)
wb.save("Operfly_BOM.xlsx")
# denetim
exp={"Core":(520,0),"Hub":(857,0),"Power":(548,0),"PC adaptörü":(392,0),"Nav":(413,520),"Radio":(384,450),"RX":(373,86),"Pilot 12":(882,86),"Air":(393,0),"Engine":(383,0),"Vision":(611,860),"Range 10":(348,50),"Range 30":(348,150),"Range 100":(348,260),"Cell":(436,250),"Pilot T":(912,86),"Pilot Pro":(1221,1796),"Base":(411,520),"Ground Radio":(494,536),"Tracker":(613,0),"Shield":(373,1342)}
tk=tm=0
for n,c,s,its in P:
    k=sum(q*PR[i][1] for i,q in its if PR[i][6]==K); m=sum(q*PR[i][1] for i,q in its if PR[i][6]==M)
    tk+=k; tm+=m
    if exp[n.replace("Operfly ","")]!=(k,m): print("FARK",n,k,m)
    else: print("%-22s %5d %5d %5d"%(n,k,m,k+m))
print("TOPLAM",tk,tm,tk+tm, "satır",LB)
acik=sum(q*PR[i][1] for n,c,s,its in P for i,q in its if PR[i][7]==A); print("acik",acik)
