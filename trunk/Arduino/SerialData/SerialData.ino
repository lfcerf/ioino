/*
Protocole d'envoie de paquets de données
lues sur un port analogique en temps réel
*/

// port lu
int port = 0;

// baudrate
int baudrate = 11520;

// taille du paquet
int taillePaquet = 100;

// paquet
int temps[taillePaquet];
int sortie[taillePaquet];

// intervalle de prélèvement (us)
int dt = 1000;

// délai d'attente effectif (recalculé à chaque loop)
int d = dt;

void setup() {
  Serial.begin(baudrate);  
}

void loop() {  
  // Construction du paquet
  for (int i=0;i<taillePaquet;i++){
    if (i == 0){
      delayMicroseconds(d);
    }
    else{
      delayMicroseconds(dt);
    }
    temps[i] = micros();              // peut être faudra-t-il inverser ces 2 lignes ...
    sortie[i] = analogRead(port);     //
  }
  // Ecriture du paquet sur le port série
  Serial.print(temps);
  Serial.print(" ");    // Caractère de séparation temps/sortie ... à voir ...
  Serial.print(sortie);
  
  // Caractère de fin de paquet
  Serial.println();
  
  // Calcul du prochain premier délai, (pour recoller le futur paquet au précédent)
  d = dt - (micros()-temps[taillePaquet-1]);
}
