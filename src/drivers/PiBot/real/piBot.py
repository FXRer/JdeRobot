# -*- coding: utf-8 -*-
from jderobot_interfaces import JdeRobotKids
import numpy
import threading
import sys, time
import jderobot_config
import progeo
import cv2

from imutils.video import VideoStream
import imutils

ORANGE_MIN = numpy.array([0, 123, 165],numpy.uint8)#numpy.array([48, 138, 138],numpy.uint8)
ORANGE_MAX = numpy.array([179, 255, 255],numpy.uint8)#numpy.array([67, 177, 192],numpy.uint8)

class PiBot:

	'''
	Controlador para el Robot PiBot de JdeRobot-Kids
	Actualmente incluye dos funciones de procesamiento visual:
	- damePosicionDeObjetoDeColor
	- dameSonarVisual
	'''
	def __init__(self, camara):
		# Libreria RPi.GPIO
		print("real")
		import RPi.GPIO as GPIO
		import pigpio # Libreria para manejar los servos
		JdeRobotKids.__init__(self)
		self._GPIO = GPIO
		self._tipo = "PiBot"
		self._dit = pigpio.pi()
		self._frame = None
		if camara == "PiCam":
			self._videostream = VideoStream(usePiCamera=True).start()
		else:
			self._videostream = VideoStream(usePiCamera=False).start()
		time.sleep(2)

	def moverServo(self, *args):
		'''
		Función que hace girar al servo motor a un angulo dado como parámetro.
		@type args: lista
		@param args: lista de argumentos:
		args[0]: puerto al que esta conectado el controlador del servo
		args[1]: banco al que esta conectado el servo en el controlador
		args[2]: angulo de giro del servo. 0-180 grados. ¡PROBAR GIRO ANTES DE MONTAR EL SERVO!
		'''
		puerto = args[0]
		banco = args[1]
		angulo = args[2]/10

		self._GPIO.setmode(GPIO.BOARD)   #Ponemos la Raspberry en modo BOARD
		self._GPIO.setup(puerto,GPIO.OUT)	#Ponemos el pin args[0] como salida
		p = self._GPIO.PWM(puerto,50)		#Ponemos el pin args[0] en modo PWM y enviamos 50 pulsos por segundo
		p.start(7.5)			   #Enviamos un pulso del 7.5% para centrar el servo
		p.ChangeDutyCycle(angulo)
		time.sleep(0.5)

	def avanzar(self, vel):
		'''
		Función que hace avanzar al robot en línea recta a una velocidad dada como parámetro.
		@type vel: entero
		@param vel: velocidad de avance del robot (máximo 255)
		'''
		#puertos donde van conectados los motores
		puertoL = 4
		puertoR = 18

		def esnegativo(vel):
			return vel < 0

		if(not esnegativo(vel)):
			#self._dit.set_servo_pulsewidth(puertoL, 1720) #hacia el frente
			#self._dit.set_servo_pulsewidth(puertoR, 1240) #hacia el frente
			if(vel <= 0.0355): #velocidad muy lenta
				self._dit.set_servo_pulsewidth(puertoL, 1529) #hacia el frente, 1526-1537
				self._dit.set_servo_pulsewidth(puertoR, 1510) #hacia el frente, 1510-1512
			elif(vel > 0.0355 and vel <= 0.0655):
				self._dit.set_servo_pulsewidth(puertoL, 1540)
				self._dit.set_servo_pulsewidth(puertoR, 1501)
			elif(vel > 0.0655 and vel <= 0.0925):
				self._dit.set_servo_pulsewidth(puertoL, 1550)
				self._dit.set_servo_pulsewidth(puertoR, 1490)
			elif(vel > 0.0925 and vel <= 0.13):
				self._dit.set_servo_pulsewidth(puertoL, 1570)
				self._dit.set_servo_pulsewidth(puertoR, 1474)
			else: #velocidad muy rapida
				self._dit.set_servo_pulsewidth(puertoL, 2500)
				self._dit.set_servo_pulsewidth(puertoR, 500)
		else:
			if(vel >= -0.0355): #velocidad muy lenta
				self._dit.set_servo_pulsewidth(puertoL, 1498)
				self._dit.set_servo_pulsewidth(puertoR, 1541)
			elif(vel < -0.0355 and vel >= -0.0655):
				self._dit.set_servo_pulsewidth(puertoL, 1490)
				self._dit.set_servo_pulsewidth(puertoR, 1545)
			elif(vel < -0.0655 and vel >= -0.0925):
				self._dit.set_servo_pulsewidth(puertoL, 1480)
				self._dit.set_servo_pulsewidth(puertoR, 1559)
			elif(vel < -0.0925 and vel >= -0.13):
				self._dit.set_servo_pulsewidth(puertoL, 1470)
				self._dit.set_servo_pulsewidth(puertoR, 1568)
			else: #velocidad muy rapida
				self._dit.set_servo_pulsewidth(puertoL, 500)
				self._dit.set_servo_pulsewidth(puertoR, 2500)

	def retroceder(self, vel):
		'''
		Función que hace retroceder al robot en línea recta a una velocidad dada como parámetro.
		@type vel: entero
		@param vel: velocidad de retroceso del robot (máximo 255)
		'''
	# Puertos de datos para servos izquierdo y derecho
		puertoL = 4
		puertoR = 18
		self._dit.set_servo_pulsewidth(puertoL, 1280)
		self._dit.set_servo_pulsewidth(puertoR, 1720)

	def parar(self):
		'''
		Función que hace detenerse al robot.
		'''
	# Puertos de datos para servos izquierdo y derecho
		puertoL = 4
		puertoR = 18
		self._dit.set_servo_pulsewidth(puertoL, 1525) #parado
		self._dit.set_servo_pulsewidth(puertoR, 1510) #parado

	def girarIzquierda(self, vel):
		'''
		Función que hace rotar al robot sobre sí mismo hacia la izquierda a una velocidad dada como parámetro.
		@type vel: entero
		@param vel: velocidad de giro del robot (máximo 255)
		'''
	# Puertos de datos para servos izquierdo y derecho
		puertoL = 4
		puertoR = 18
		self._dit.set_servo_pulsewidth(puertoL, 1525) #parado
		self._dit.set_servo_pulsewidth(puertoR, 1380) #avanza al frente

	def girarDerecha(self, vel):
		'''
		Función que hace rotar al robot sobre sí mismo hacia la derecha a una velocidad dada como parámetro.
		@type vel: entero
		@param vel: velocidad de giro del robot (máximo 255)
		'''
	# Puertos de datos para servos izquierdo y derecho
		puertoL = 4
		puertoR = 18
		self._dit.set_servo_pulsewidth(puertoL, 1620) #avanza al frente
		self._dit.set_servo_pulsewidth(puertoR, 1510) #parado

        def move(self, velV, velW):
		'''
		Función que hace avanzar y girar al robot al mismo tiempo, según las velocidades V,W dadas como parámetro.

		@type velV, velW: enteros de [1 a 5, a mas, se corta en 5]
		@param velV, velW: velocidades de avance de motores lineal y angular, en m/s y rad/s respectivamente
		'''
		# Puertos de datos para servos izquierdo y derecho
		puertoL = 4
		puertoR = 18

		def esnegativo(n):
			return n < 0

		def espositivo(n):
			return n > 0

		def escero(n):
			return n == 0

		def movermotorizq(vel):

			if(not esnegativo(vel)):

				if(escero(vel)):
					self._dit.set_servo_pulsewidth(puertoL, 1510) #parado 1525
				elif(vel <= 0.0355): #velocidad muy lenta
					self._dit.set_servo_pulsewidth(puertoL, 1529) #hacia el frente, 1526-1537
				elif(vel > 0.0355 and vel <= 0.0655):
					self._dit.set_servo_pulsewidth(puertoL, 1540)
				elif(vel > 0.0655 and vel <= 0.0925):
					self._dit.set_servo_pulsewidth(puertoL, 1550)
				elif(vel > 0.0925 and vel <= 0.13):
					self._dit.set_servo_pulsewidth(puertoL, 1570)
				else: #velocidad muy rapida
					self._dit.set_servo_pulsewidth(puertoL, 2500)
			else:
				if(vel >= -0.0355): #velocidad muy lenta
					self._dit.set_servo_pulsewidth(puertoL, 1498)
				elif(vel < -0.0355 and vel >= -0.0655):
					self._dit.set_servo_pulsewidth(puertoL, 1490)
				elif(vel < -0.0655 and vel >= -0.0925):
					self._dit.set_servo_pulsewidth(puertoL, 1480)
				elif(vel < -0.0925 and vel >= -0.13):
					self._dit.set_servo_pulsewidth(puertoL, 1470)
				else: #velocidad muy rapida
					self._dit.set_servo_pulsewidth(puertoL, 500)

		def movermotordcho(vel):

			if(not esnegativo(vel)):

				if(escero(vel)):
					self._dit.set_servo_pulsewidth(puertoR, 1525) #parado 1510
				if(vel <= 0.0355): #velocidad muy lenta
					self._dit.set_servo_pulsewidth(puertoR, 1510) #hacia el frente, 1510-1512
				elif(vel > 0.0355 and vel <= 0.0655):
					self._dit.set_servo_pulsewidth(puertoR, 1501)
				elif(vel > 0.0655 and vel <= 0.0925):
					self._dit.set_servo_pulsewidth(puertoR, 1490)
				elif(vel > 0.0925 and vel <= 0.13):
					self._dit.set_servo_pulsewidth(puertoR, 1474)
				else: #velocidad muy rapida
					self._dit.set_servo_pulsewidth(puertoR, 500)
			else:
				if(vel >= -0.0355): #velocidad muy lenta
					self._dit.set_servo_pulsewidth(puertoR, 1541)
				elif(vel < -0.0355 and vel >= -0.0655):
					self._dit.set_servo_pulsewidth(puertoR, 1545)
				elif(vel < -0.0655 and vel >= -0.0925):
					self._dit.set_servo_pulsewidth(puertoR, 1559)
				elif(vel < -0.0925 and vel >= -0.13):
					self._dit.set_servo_pulsewidth(puertoR, 1568)
				else: #velocidad muy rapida
					self._dit.set_servo_pulsewidth(puertoR, 2500)

		#Aqui empieza la algoritmia principal

		if(velW != 0):
			rcir = abs(velV / velW) #Es el radio de la circunferencia que tengo que trazar. En valor absoluto
			velmotorgiro = abs(velV) + rcir     #Velocidad a la que tiene que girar el motor encargado del giro del robot
		if(escero(velV) and not escero(velW)):
			#Motor izquierdo hacia atras y motor derecho hacia adelante a velocidad maxima
			if(espositivo(velW)):
				movermotordcho(1)
				movermotorizq(-1)
			else:
				movermotordcho(-1)
				movermotorizq(1)

		elif(not escero(velV) and escero(velW)):
			#Avanza hacia el frente a la velocidad lineal dada
			movermotordcho(velV)
			movermotorizq(velV)

		elif(espositivo(velV) and espositivo(velW)):
			movermotorizq(velV)
			movermotordcho(velmotorgiro)
		elif(espositivo(velV) and esnegativo(velW)):
			movermotorizq(velmotorgiro)
			movermotordcho(velV)
		elif(esnegativo(velV) and espositivo(velW)):
			movermotorizq(-velmotorgiro)
			movermotordcho(velV)
		elif(esnegativo(velV) and esnegativo(velW)):
			movermotorizq(velV)
			movermotordcho(-velmotorgiro)

	def leerangulorueda(self, Encoder):
	#devuelve el angulo en el que se encuentra la rueda cuyo pin de feedback
	#se encuentra en el pin "Encoder" en el momento en que se llama a la funcion

		#Constantes:
		DcMin = 29
		DcMax = 971
		Pi = 3.1416
		FullCircle = 2 * Pi
		DutyScale = 1000
		Q2Min = FullCircle / 4 #angulo minimo perteneciente al segundo cuadrante
		Q3Max = Q2Min * 3 #angulo maximo perteneciente al tercer cuadrante

		turns = 0

		def pulse_in(inp, bit):

		    def readuntil(inp, bit):
				rec = self._GPIO.input(inp)
				if(rec == bit):
				    #esperar hasta terminar de leer unos
				    while(rec == bit):
					rec = self._GPIO.input(inp)
				#leer ceros hasta que me llegue el primer uno
				if(bit == 1):
				    while(rec == 0):
					rec = self._GPIO.input(inp)
				    #ahora me acaba de llegar el primer uno despues de los ceros
				else:
				    while(rec == 1):
					rec = self._GPIO.input(inp)
				    #ahora me acaba de llegar el primer cero despues de los unos

		    if(bit != 0 and bit != 1):
			    return 0
		    else:
		    	readuntil(inp, bit) #leo hasta que me llega ese bit
		    	start = time.time() #guardo la hora actual
			if(bit == 1):
			    readuntil(inp, 0) #leo hasta que me llega un bit contrario al anterior
			else:
			    readuntil(inp, 1)
			finish = time.time()
			elapsed = (finish - start) * 1000000 #tiempo en microsegundos

			return elapsed #todavia esto no son microsegundos. Hay que pasarlo

		def initangle():
		    timeHigh = pulse_in(Encoder, 1) #devuelve el tiempo en microsegundos
		    timeLow = pulse_in(Encoder, 0) #devuelve el tiempo en microsegundos
		    timeCycle = timeHigh + timeLow
		    dutyCycle = (DutyScale * timeHigh) / timeCycle #calculo el ciclo de trabajo
		    return (FullCircle - 1) - ((dutyCycle - DcMin) * FullCircle) / (DcMax - DcMin + 1)


		#se inicializa la configuracion de los pines correspondientes:
		self._GPIO.setmode(self._GPIO.BCM)
		self._GPIO.setup(Encoder, self._GPIO.IN)


		#calculo el angulo inicial
		angle = initangle()
		p_angle = angle

		finish = False
		while(not finish):
		    timeHigh = pulse_in(Encoder, 1) #devuelve el tiempo en microsegundos
		    timeLow = pulse_in(Encoder, 0) #devuelve el tiempo en microsegundos

		    timeCycle = timeHigh + timeLow

		    if((timeCycle > 1000) and (timeCycle < 1200)):
			finish = True

		dutyCycle = (DutyScale * timeHigh)/ timeCycle #calculo el ciclo de trabajo

		angle = (FullCircle - 1) - ((dutyCycle - DcMin) * FullCircle) / (DcMax - DcMin + 1)
		if(angle < 0):
		   	angle = 0
	 	elif(angle > (FullCircle - 1)):
		    angle = FullCircle - 1

		#Si la transicion va del cuarto cuadrante al primero, incremento 'turns'
		if((angle < Q2Min) and (p_angle > Q3Max)):
		    turns = turns + 1
		#Si la transicion va del primer cuadrante al cuarto, incremento 'turns'
		elif((p_angle < Q2Min) and (angle > Q3Max)):
		    turns = turns - 1

		#Calculo el angulo
		if(turns >= 0):
		    angle = (turns * FullCircle) + angle
		elif(turns <  0):
		    angle = ((turns + 1) * FullCircle) - (FullCircle - angle)
		#Esto lo hago para que cuando repita la vuelta se ponga a cero de nuevo
		if(angle >= FullCircle):
		    angle = angle - FullCircle
		    turns = 0
		elif(angle <= -FullCircle):
		    angle = angle + FullCircle
		    turns = 0

		return angle

	def leerIRSigueLineas(self): #devuelve el estado de los sensores IR

		right_sensor_port = 22
		left_sensor_port = 27

		self._GPIO.setmode(self._GPIO.BCM)
		self._GPIO.setup(right_sensor_port, self._GPIO.IN)
		self._GPIO.setup(left_sensor_port, self._GPIO.IN)
		right_value = self._GPIO.input(right_sensor_port)
		left_value = self._GPIO.input(left_sensor_port)
		#0: ambos sobre la linea
		#1: izquierdo sobre la linea
		#2: derecho sobre la linea
		#3: ambos fuera de la linea

		if(right_value == 1 and left_value == 1):
			state = 0
		elif(right_value == 0 and left_value == 1):
			state = 1
		elif(right_value == 1 and left_value == 0):
			state = 2
		else:
			state = 3

		return state

	def leerUltrasonido(self): #devuelve la distancia a un objeto en metros

		inp = 3
		out = 2

		self._GPIO.setwarnings(False)
		self._GPIO.setmode(self._GPIO.BCM)
		self._GPIO.setup(out, self._GPIO.OUT)
		self._GPIO.setup(inp, self._GPIO.IN)

		self._GPIO.output(out, False)
		time.sleep(0.00001)
		self._GPIO.output(out, True)
		time.sleep(0.00001)
		self._GPIO.output(out, False)
		start = time.time()
		while(self._GPIO.input(inp) == 0):
		    start = time.time()
		while(self._GPIO.input(inp) == 1):
		    stop = time.time()
		elapsed = stop - start

		return (elapsed * 343) / 2

	def dameImagen (self):
		self._frame = self._videostream.read()
		self._frame = imutils.resize(self._frame, width=400)

		return self._frame

	def mostrarImagen (self):
		cv2.imshow("Imagen", self._frame)

	def dameObjeto(self, lower=ORANGE_MIN, upper=ORANGE_MAX, showImageFiltered=False):
		'''
		Función que devuelve el centro del objeto que tiene un color verde en el rango [GREEN_MIN, GREEN_MAX] para ser detectado
		'''
		# resize the image
		image = self.dameImagen()

		# convert to the HSV color space
		hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

		# construct a mask for the color specified
		# then perform a series of dilations and erosions
		# to remove any small blobs left in the mask
		mask = cv2.inRange(hsv, ORANGE_MIN, ORANGE_MAX)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)

		# find contours in the mask and
		# initialize the current center
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
		center = None

		# only proceed if at least one contour was found
		if len(cnts) > 0:
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle and
			# centroid
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)
			M = cv2.moments(c)
			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
			area = M["m00"]

			# only proceed if the radius meets a minimum size
			if radius > 10:
				# draw the circle border
				cv2.circle(image, (int(x), int(y)), int(radius), (0, 255, 0), 2)

				# and the centroid
				cv2.circle(image, center, 5, (0, 255, 255), -1)
		if showImageFiltered:
			# Control waitKey from outside, only for local executions, not jupyter.
			cv2.imshow("image_filtered", image)
			cv2.imshow("mask", mask)

		return center, area

	def dameSonarVisual ():
		'''
		Función que devuelve el array de puntos [X,Y] (Z=0) correspondiente al obstáculo detectado
		'''
		cameraModel = loadPiCamCameraModel ()
		puntosFrontera = 0
		fronteraArray = numpy.zeros((ANCHO_IMAGEN,2), dtype = "float64")

		image = dameImagen ()
		hsvImg = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
		bnImg = cv2.inRange(hsvImg, GREEN_MIN, GREEN_MAX)

		pixel = Punto2D()
		pixelOnGround3D = Punto3D()
		tmp2d = Punto2D()
		puntosFrontera = 0
		j = 0

		# Ground image: recorremos la imagen de abajo a arriba (i=filas) y de izquierda a derecha (j=columnas)
		while (j < ANCHO_IMAGEN): # recorrido en columnas
			i = LARGO_IMAGEN-1
			esFrontera = None
			while ((i>=0) and (esFrontera == None)): # recorrido en filas
				pos = i*ANCHO_IMAGEN+j # posicion actual

				pix = bnImg[i, j] # value 0 or 255 (frontera)

				if (pix != 0): # si no soy negro
					esFrontera = True # lo damos por frontera en un principio, luego veremos
					# Calculo los demás vecinos, para ver de qué color son...
					c = j - 1
					row = i
					v1 = row*ANCHO_IMAGEN+c

					if (not((c >= 0) and (c < ANCHO_IMAGEN) and
					(row >= 0) and (row < LARGO_IMAGEN))): # si no es válido ponemos sus valores a 0
						pix = 0
					else:
						pix = bnImg[row, c]

					if (esFrontera == True): # si NO SOY COLOR CAMPO y alguno de los vecinitos ES color campo...
						pixel.x = j
						pixel.y = i
						pixel.h = 1

						# obtenemos su backproject e intersección con plano Z en 3D
						pixelOnGround3D = getIntersectionZ (pixel, cameraModel)

						# vamos guardando estos puntos frontera 3D para luego dibujarlos con PyGame
						fronteraArray[puntosFrontera][0] = pixelOnGround3D.x
						fronteraArray[puntosFrontera][1] = pixelOnGround3D.y
						puntosFrontera = puntosFrontera + 1
						#print "Hay frontera en pixel [",i,",",j,"] que intersecta al suelo en [",pixelOnGround3D.x,",",pixelOnGround3D.y,",",pixelOnGround3D.z,"]"

				i = i - 1
			j = j + 5

		return fronteraArray

	def quienSoy(self):
		print ("Yo soy un robot real PiBot")

	@property
	def tipo(self):
		return self._tipo

	@tipo.setter
	def tipo(self, valor):
		self._tipo = valor
