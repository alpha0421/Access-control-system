# Access-control-system
門禁系統

偵測端：
    2019/05/24 版本1-偵測RFID，並將其UID上傳至Azure Table-RFID中

    2019/05/28 最終版本(MFRC522-Final)-偵測RFID，並將其UID上傳至Azure Table中

      (1) Projects-CheckID

      (2) RFID(作為log表)

作動端：

    程式：RFID_Client

    使用GPIO接腳7，依照Projects-Door Value亮暗燈
