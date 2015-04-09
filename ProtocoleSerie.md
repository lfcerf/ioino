#Description du protocole de communication en temps réel

# Protocole série #

## Paramètres du port ##

  * port – Device name or port number number or None.
  * baudrate – Baud rate such as 9600 or 115200 etc.
  * bytesize – Number of data bits. Possible values: FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS
  * parity – Enable parity checking. Possible values: PARITY\_NONE, PARITY\_EVEN, PARITY\_ODD PARITY\_MARK, PARITY\_SPACE
  * stopbits – Number of stop bits. Possible values: STOPBITS\_ONE, STOPBITS\_ONE\_POINT\_FIVE, STOPBITS\_TWO
  * timeout – Set a read timeout value.
  * xonxoff – Enable software flow control.
  * rtscts – Enable hardware (RTS/CTS) flow control.
  * dsrdtr – Enable hardware (DSR/DTR) flow control.
  * writeTimeout – Set a write timeout value.
  * interCharTimeout – Inter-character timeout, None to disable (default).

## Format des données ##

Envoie de l'état d'un port de l'Arduino (analogique ou numérique) par paquets.
  * point = temps horloge Arduino + valeur sur le port
> > 2 octets              + 2 octets(port A) ou 1 octet (port N)
  * taille des paquets : à définir ...
  * caractère de fin de paquet : LR

## Codes Arduino ##
  * [Version beta de code Arduino de transfert de paquets](http://ioino.googlecode.com/svn/trunk/Arduino/SerialData/SerialData.ino).