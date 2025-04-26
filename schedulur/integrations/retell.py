import os
from retell import Retell

retell = Retell(api_key=os.environ["RETELL_API_KEY"])

def call_doctor(to_number, user_name, doctor_name, insurance_type):
  try:
    response = retell.call.create_phone_call(
      from_number=os.environ["RETELL_FROM_NUMBER"],
      to_number=to_number,
      override_agent_id=os.environ["RETELL_AGENT_ID"],
      retell_llm_dynamic_variables={
        "user": user_name,
        "doctor_name": doctor_name,
        "insurance_type": insurance_type
      }
    )
    print(f"Call initiated: {response}")
  except Exception as e:
    print(f"Error making call: {e}")

def receive_webhook(call_data):
  print(call_data)