int ledPin = 4; // LED conectado al pin 4
int buttonPin = 3; // Botón conectado al pin 3
int led2Pin = 2; // LED conectado al pin 2

bool led2_state = false; // Estado del LED del pin 2

void setup() {
  pinMode(ledPin, OUTPUT); // Configura el pin del LED como salida
  pinMode(buttonPin, INPUT_PULLUP); // Configura el pin del botón como entrada con pull-up
  pinMode(led2Pin, OUTPUT); // Configura el pin del segundo LED como salida
  pinMode(6, OUTPUT);
  Serial.begin(9600); // Inicia la comunicación serial a 9600 baudios
}

void loop() {

  digitalWrite(6, HIGH);

  // Maneja la comunicación serial
  handleSerialInput();

  // Maneja el estado del LED del pin 2
  updateLed2State();

  // Controla los LEDs basado en el botón
  if (digitalRead(buttonPin) == LOW) {
    digitalWrite(ledPin, LOW); // Apaga el LED del pin 4
    digitalWrite(led2Pin, HIGH); // Enciende el LED del pin 2
    led2_state = true; // Actualiza el estado del LED del pin 2
  }
}

void handleSerialInput() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'H') {
      digitalWrite(ledPin, HIGH); // Enciende el LED
    } else if (command == 'L') {
      digitalWrite(ledPin, LOW); // Apaga el LED
    } else if (command == 'C') {
      if (digitalRead(buttonPin) == LOW) {
        Serial.write('1'); // Envía '1' si el botón en el pin 3 está presionado
      } else {
        Serial.write('0'); // Envía '0' si el botón en el pin 3 no está presionado
      }
    } else if (command == 'P') {
      led2_state = true;
      digitalWrite(led2Pin, HIGH); // Enciende el LED del pin 2
    } else if (command == 'Q') {
      led2_state = false;
      digitalWrite(led2Pin, LOW); // Apaga el LED del pin 2
    }
  }
}

void updateLed2State() {
  if (led2_state) {
    digitalWrite(led2Pin, HIGH); // Mantiene el LED del pin 2 encendido
  }
}
