from .models import Dht11
from .serializers import DHT11serialize
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
import requests

# Définir la fonction pour envoyer des messages Telegram
def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, data=payload)
    return response

@api_view(["GET", "POST"])
def Dlist(request):
    if request.method == "GET":
        all_data = Dht11.objects.all()
        data_ser = DHT11serialize(all_data, many=True)  # Les données sont sérialisées en JSON
        return Response(data_ser.data)

    elif request.method == "POST":
        serial = DHT11serialize(data=request.data)

        if serial.is_valid():
            serial.save()  # Sauvegarde les données
            derniere_temperature = Dht11.objects.last().temp  # Récupère la dernière température
            print(f"Dernière température : {derniere_temperature}")

            # Vérifier si la température est valide avant de comparer
            if derniere_temperature is not None and derniere_temperature > 25:
                # Alert Email
                # subject = 'Alerte : Température Élevée'
                # message = 'La température dépasse le seuil de 25°C, veuillez intervenir immédiatement pour vérifier et corriger cette situation'
                # email_from = settings.EMAIL_HOST_USER
                # recipient_list = ['hanae.mouhib14@gmail.com']
                # send_mail(subject, message, email_from, recipient_list)

                # Alert WhatsApp
                account_sid = 'ACfae1cbb691983f07ef0e851195c87bd8'
                auth_token = '615af220db7da551b67d75f1fd8dc6c2'
                client = Client(account_sid, auth_token)
                message_whatsapp = client.messages.create(
                    from_='whatsapp:+14155238886',
                    body='La température dépasse le seuil de 25°C, veuillez intervenir immédiatement pour vérifier et corriger cette situation',
                    to='whatsapp:+212616980714'
                )
                print("Message WhatsApp envoyé.")

                # Alert Telegram
                # telegram_token = 'votre_token'
                # chat_id = 'votre_chat_id'  # Remplacez par votre ID de chat
                # telegram_message = 'La température dépasse le seuil de 25°C, veuillez intervenir immédiatement pour vérifier et corriger cette situation'
                # send_telegram_message(telegram_token, chat_id, telegram_message)
                # print("Message Telegram envoyé.")

            else:
                print("Température normale ou non définie.")

            return Response(serial.data, status=status.HTTP_201_CREATED)

        else:
            return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)
