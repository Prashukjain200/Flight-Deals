from flask import Flask, render_template, redirect, url_for
import requests
from datetime import datetime, timedelta
from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
import email_validator
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = '49itk5krtgktpr5ktgprkyh'

class FirstForm(FlaskForm):
    IATACode = StringField("IATA Code", validators=[DataRequired()])
    number = StringField("Number", validators=[DataRequired()])
    submit = SubmitField("Get Deals")

class SecondForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")


@app.route('/', methods=["GET", "POST"])
def get_all_deals():
    form = FirstForm()
    if form.validate_on_submit():
        iata = form.IATACode.data
        number = form.number.data

        ORIGIN_CITY_IATA = iata
        data_manager = DataManager()
        flight_search = FlightSearch()
        notification_manager = NotificationManager(number)

        sheet_data = data_manager.get_destination_data()

        if sheet_data[0]["iataCode"] == "":
            city_names = [row["city"] for row in sheet_data]
            data_manager.city_codes = flight_search.get_destination_codes(city_names)
            data_manager.update_destination_codes()
            sheet_data = data_manager.get_destination_data()

        destinations = {
            data["iataCode"]: {
                "id": data["id"],
                "city": data["city"],
                "price": data["lowestPrice"]
            } for data in sheet_data}

        tomorrow = datetime.now() + timedelta(days=1)
        six_month_from_today = datetime.now() + timedelta(days=6 * 30)

        for destination_code in destinations:
            flight = flight_search.check_flights(
                ORIGIN_CITY_IATA,
                destination_code,
                from_time=tomorrow,
                to_time=six_month_from_today
            )
            print(flight.price)
            if flight is None:
                continue

            if flight.price < destinations[destination_code]["price"]:
                print("Hello")
                users = data_manager.get_customer_emails()
                emails = [row["email"] for row in users]
                names = [row["firstName"] for row in users]
                print("Hello")

                message = f"Low price alert! Only £{flight.price} to fly from {flight.origin_city}-{flight.origin_airport} to {flight.destination_city}-{flight.destination_airport}, from {flight.out_date} to {flight.return_date}."

                if flight.stop_overs > 0:
                    message += f"\nFlight has {flight.stop_overs} stop over, via {flight.via_city}."

                link = f"https://www.google.co.uk/flights?hl=en#flt={flight.origin_airport}.{flight.destination_airport}.{flight.out_date}*{flight.destination_airport}.{flight.origin_airport}.{flight.return_date}"

                notification_manager.send_emails(emails, message, link)
                return redirect(url_for("get_all_deals"))
    return render_template("index.html", form=form)


@app.route("/newsletter", methods=["GET", "POST"])
def newsletter():
    form = SecondForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email_id = form.email.data

        SHEETY_USERS_ENDPOINT = "https://api.sheety.co/08eeb98a6938122256022a21f0f697ab/users/sheet1/"

        first = first_name
        last = last_name
        email = email_id
        new_data = {
            "sheet1": {
                "firstName": first,
                "lastName": last,
                "email": email
            }
        }
        response = requests.post(
            url=f"{SHEETY_USERS_ENDPOINT}",
            json=new_data
        )
        print(response.text)
        return redirect(url_for("newsletter"))
    return render_template("newsletter.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)

