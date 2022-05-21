#define echoPin 2 // ECHO na D2
#define trigPin 3 //TRIG na D3
#define LedPin 6

// definovanie premennych
long duration;
int distance; 
int zadHod = 10;
long m;
void setup() {
  pinMode(trigPin, OUTPUT); 
  pinMode(echoPin, INPUT); 
  pinMode(LedPin, OUTPUT);
  Serial.begin(9600); 

}
void loop() {
  //zadHod = 10;
  if(Serial.available()) {
    zadHod = Serial.readString().toInt();
    Serial.println(zadHod);
  }
  
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2; 
  Serial.println(distance);

  
  if(distance >= zadHod && distance < 61){
    m = map(distance, 60, zadHod, 0, 255);
  }
  else{ m = 0;}
  analogWrite(LedPin, m);
  
}
