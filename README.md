# Anonim-Chat-V1.0
Anonim Chat App

Versiyon 1.0:

Backend: WebSocket endpoint açtık.
ConnectionManager: tüm bağlı kullanıcıları takip ediyor.
broadcast(): herkesin mesajı görmesini sağlıyor.
HTML client: test için basit bir chat arayüzü.

Versiyon 1.1:

Herkese mesaj yerine oda bazlı mesajlaşma kurduk.
Bu, bizim “eşleşme” mantığının temelini oluşturuyor.

Versiyon 1.2:

İlk bağlanan → “Beklemeye alındın” mesajı görür.
İkinci bağlanan → rastgele (aslında sıradaki) kişiyle eşleşir.
Artık iki taraf birbirine mesaj gönderebilir.
Üçüncü kişi bağlanırsa, o da başka biriyle eşleşene kadar bekler.

Versiyon 1.3:

Basit bir register sistemi kurduk (şimdilik RAM’de).
Admin paneli ekledik.
Eşleştirme butonu admin tarafından tetiklendi.
Kullanıcılar sadece ID ile eşleşip konuşabiliyor.
