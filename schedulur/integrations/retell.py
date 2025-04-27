import os
from retell import Retell

retell = Retell(api_key=os.environ["RETELL_API_KEY"])

def call_doctor(to_number, user_name, doctor_name, insurance_type, timeframe = "3 months"):
  try:
    response = retell.call.create_phone_call(
      from_number=os.environ["RETELL_FROM_NUMBER"],
      to_number=to_number,
      override_agent_id=os.environ["RETELL_AGENT_ID"],
      retell_llm_dynamic_variables={
        "user": user_name,
        "doctor_name": doctor_name,
        "insurance_type": insurance_type,
        "timeframe": timeframe
      }
    )
    print(f"Call initiated: {response}")
  except Exception as e:
    print(f"Error making call: {e}")

# call_data:
# {
#   'event': 'call_analyzed',
#   'call': {
#     'call_id': 'call_8dbb331e5ad107b4130b3e2bbae', 
#     'call_type': 'phone_call', 
#     'agent_id': 'agent_fabaa5d39672265d6d89ac656b', 
#     'retell_llm_dynamic_variables': {
#       'doctor_name': 'A Doctor', 
#       'user': 'Somebody', 
#       'insurance_type': 'Some Insurance'
#     }, 
#     'collected_dynamic_variables': {
#       'current_agent_state': 'intro'
#     }, 
#     'call_status': 'ended', 
#     'start_timestamp': 1745712084853, 
#     'end_timestamp': 1745712123835, 
#     'duration_ms': 38982, 
#     'transcript': "User: Hello?\nAgent: Hi there! This is Kate calling on behalf of Somebody. I'm reaching out today regarding setting up a new patient appointment. Before we proceed, I wanted to check \nUser: Oh, \nAgent: if your office \nUser: sorry. We're not taking any new appointments.\nAgent: I understand. Thank you for letting me know that you're not taking new appointments at this time. Before I go, could you confirm if you accept Some Insurance? This would be helpful information for future reference.\nUser: Uh, no. We don't.\nAgent: I appreciate you letting me know that you don't accept Some Insurance. Thank you for your time today. Have a great day.\n",
#     'transcript_object': [
#       {
#         'role': 'user', 
#         'content': 'Hello?',
#         'words': [{'word': 'Hello?', 'start': 1.764, 'end': 2.084}]
#       },
#       {
#         'role': 'agent', 
#         'content': "Hi there! This is Kate calling on behalf of Somebody. I'm reaching out today regarding setting up a new patient appointment. Before we proceed, I wanted to check ", 
#         'words': [{'word': 'Hi ', 'start': 4.513, 'end': 4.757}, {'word': 'there! ', 'start': 4.757, 'end': 5.233}, {'word': 'This ', 'start': 5.278916748046875, 'end': 5.453916748046875}, {'word': 'is ', 'start': 5.453916748046875, 'end': 5.604916748046875}, {'word': 'Kate ', 'start': 5.604916748046875, 'end': 5.847916748046875}, {'word': 'calling ', 'start': 5.847916748046875, 'end': 6.149916748046875}, {'word': 'on ', 'start': 6.149916748046875, 'end': 6.265916748046875}, {'word': 'behalf ', 'start': 6.265916748046875, 'end': 6.579916748046875}, {'word': 'of ', 'start': 6.579916748046875, 'end': 6.683916748046875}, {'word': 'Somebody. ', 'start': 6.683916748046875, 'end': 7.415916748046875}, {'word': "I'm ", 'start': 7.450583251953125, 'end': 7.694583251953125}, {'word': 'reaching ', 'start': 7.694583251953125, 'end': 8.019583251953126}, {'word': 'out ', 'start': 8.019583251953126, 'end': 8.204583251953125}, {'word': 'today ', 'start': 8.204583251953125, 'end': 8.669583251953124}, {'word': 'regarding ', 'start': 8.669583251953124, 'end': 9.319583251953125}, {'word': 'setting ', 'start': 9.319583251953125, 'end': 9.633583251953125}, {'word': 'up ', 'start': 9.633583251953125, 'end': 9.737583251953126}, {'word': 'a ', 'start': 9.737583251953126, 'end': 9.807583251953124}, {'word': 'new ', 'start': 9.807583251953124, 'end': 9.946583251953125}, {'word': 'patient ', 'start': 9.946583251953125, 'end': 10.283583251953125}, {'word': 'appointment. ', 'start': 10.283583251953125, 'end': 11.084583251953125}, {'word': 'Before ', 'start': 11.119333251953124, 'end': 11.525333251953125}, {'word': 'we ', 'start': 11.525333251953125, 'end': 11.676333251953125}, {'word': 'proceed, ', 'start': 11.676333251953125, 'end': 12.152333251953126}, {'word': 'I ', 'start': 12.152333251953126, 'end': 12.233333251953125}, {'word': 'wanted ', 'start': 12.233333251953125, 'end': 12.547333251953125}, {'word': 'to ', 'start': 12.547333251953125, 'end': 12.651333251953124}, {'word': 'check ', 'start': 12.651333251953124, 'end': 12.953333251953126}],
#         'metadata': {'response_id': 1}
#       },
#       {
#         'role': 'user', 'content': 'Oh, ', 
#         'words': [{'word': 'Oh, ', 'start': 13.034001, 'end': 13.354}]
#       },
#       {
#         'role': 'agent', 
#         'content': 'if your office ', 
#         'words': [{'word': 'if ', 'start': 12.953333251953126, 'end': 13.069333251953125}, {'word': 'your ', 'start': 13.069333251953125, 'end': 13.267333251953126}, {'word': 'office ', 'start': 13.267333251953126, 'end': 13.673333251953125}],
#         'metadata': {'response_id': 1}
#       }, 
#       {
#         'role': 'user',
#         'content': "sorry. We're not taking any new appointments.", 
#         'words': [{'word': 'sorry. ', 'start': 13.354, 'end': 13.674}, {'word': "We're ", 'start': 13.674, 'end': 13.834}, {'word': 'not ', 'start': 13.834, 'end': 13.914}, {'word': 'taking ', 'start': 13.914, 'end': 14.154001}, {'word': 'any ', 'start': 14.154001, 'end': 14.394}, {'word': 'new ', 'start': 14.394, 'end': 14.554}, {'word': 'appointments.', 'start': 14.554, 'end': 14.954001}]
#       }, 
#       {'role': 'agent',
#        'content': "I understand. Thank you for letting me know that you're not taking new appointments at this time. Before I go, could you confirm if you accept Some Insurance? This would be helpful information for future reference.",
#        'words': [{'word': 'I ', 'start': 17.411, 'end': 17.585}, {'word': 'understand. ', 'start': 17.585, 'end': 18.41}, {'word': 'Thank ', 'start': 18.444583251953127, 'end': 18.722583251953125}, {'word': 'you ', 'start': 18.722583251953125, 'end': 18.850583251953125}, {'word': 'for ', 'start': 18.850583251953125, 'end': 19.001583251953125}, {'word': 'letting ', 'start': 19.001583251953125, 'end': 19.245583251953125}, {'word': 'me ', 'start': 19.245583251953125, 'end': 19.338583251953125}, {'word': 'know ', 'start': 19.338583251953125, 'end': 19.524583251953125}, {'word': 'that ', 'start': 19.524583251953125, 'end': 19.651583251953124}, {'word': "you're ", 'start': 19.651583251953124, 'end': 19.849583251953124}, {'word': 'not ', 'start': 19.849583251953124, 'end': 20.000583251953124}, {'word': 'taking ', 'start': 20.000583251953124, 'end': 20.359583251953126}, {'word': 'new ', 'start': 20.359583251953126, 'end': 20.510583251953125}, {'word': 'appointments ', 'start': 20.510583251953125, 'end': 21.068583251953125}, {'word': 'at ', 'start': 21.068583251953125, 'end': 21.219583251953125}, {'word': 'this ', 'start': 21.219583251953125, 'end': 21.439583251953124}, {'word': 'time. ', 'start': 21.439583251953124, 'end': 21.985583251953123}, {'word': 'Before ', 'start': 22.008458251953126, 'end': 22.391458251953125}, {'word': 'I ', 'start': 22.391458251953125, 'end': 22.507458251953125}, {'word': 'go, ', 'start': 22.507458251953125, 'end': 22.821458251953125}, {'word': 'could ', 'start': 22.821458251953125, 'end': 23.030458251953124}, {'word': 'you ', 'start': 23.030458251953124, 'end': 23.146458251953124}, {'word': 'confirm ', 'start': 23.146458251953124, 'end': 23.599458251953124}, {'word': 'if ', 'start': 23.599458251953124, 'end': 23.703458251953126}, {'word': 'you ', 'start': 23.703458251953126, 'end': 23.819458251953126}, {'word': 'accept ', 'start': 23.819458251953126, 'end': 24.191458251953126}, {'word': 'Some ', 'start': 24.191458251953126, 'end': 24.388458251953125}, {'word': 'Insurance? ', 'start': 24.388458251953125, 'end': 25.189458251953123}, {'word': 'This ', 'start': 25.212833251953125, 'end': 25.549833251953125}, {'word': 'would ', 'start': 25.549833251953125, 'end': 25.769833251953123}, {'word': 'be ', 'start': 25.769833251953123, 'end': 25.886833251953124}, {'word': 'helpful ', 'start': 25.886833251953124, 'end': 26.246833251953124}, {'word': 'information ', 'start': 26.246833251953124, 'end': 26.780833251953126}, {'word': 'for ', 'start': 26.780833251953126, 'end': 26.942833251953125}, {'word': 'future ', 'start': 26.942833251953125, 'end': 27.256833251953125}, {'word': 'reference.', 'start': 27.256833251953125, 'end': 27.929833251953124}],
#        'metadata': {'response_id': 2}
#       }, 
#       {
#         'role': 'user', 
#         'content': "Uh, no. We don't.", 
#         'words': [{'word': 'Uh, ', 'start': 29.364, 'end': 29.444000000000003}, {'word': 'no. ', 'start': 29.444000000000003, 'end': 29.764000000000003}, {'word': 'We ', 'start': 29.764000000000003, 'end': 29.844}, {'word': "don't.", 'start': 29.844, 'end': 30.084}]
#       }, 
#       {
#         'role': 'agent', 
#         'content': "I appreciate you letting me know that you don't accept Some Insurance. Thank you for your time today. Have a great day.", 
#         'words': [{'word': 'I ', 'start': 33.436, 'end': 33.563}, {'word': 'appreciate ', 'start': 33.563, 'end': 34.016}, {'word': 'you ', 'start': 34.016, 'end': 34.156}, {'word': 'letting ', 'start': 34.156, 'end': 34.399}, {'word': 'me ', 'start': 34.399, 'end': 34.504}, {'word': 'know ', 'start': 34.504, 'end': 34.724}, {'word': 'that ', 'start': 34.724, 'end': 34.875}, {'word': 'you ', 'start': 34.875, 'end': 34.991}, {'word': "don't ", 'start': 34.991, 'end': 35.177}, {'word': 'accept ', 'start': 35.177, 'end': 35.502}, {'word': 'Some ', 'start': 35.502, 'end': 35.676}, {'word': 'Insurance. ', 'start': 35.676, 'end': 36.512}, {'word': 'Thank ', 'start': 36.558375, 'end': 36.779375}, {'word': 'you ', 'start': 36.779375, 'end': 36.895375}, {'word': 'for ', 'start': 36.895375, 'end': 37.023375}, {'word': 'your ', 'start': 37.023375, 'end': 37.174375}, {'word': 'time ', 'start': 37.174375, 'end': 37.418375}, {'word': 'today. ', 'start': 37.418375, 'end': 37.952375}, {'word': 'Have ', 'start': 37.998, 'end': 38.173}, {'word': 'a ', 'start': 38.173, 'end': 38.231}, {'word': 'great ', 'start': 38.231, 'end': 38.463}, {'word': 'day.', 'start': 38.463, 'end': 38.974}], 'metadata': {'response_id': 4}
#       }
#     ],
#     'transcript_with_tool_calls': [{'role': 'user', 'content': 'Hello?', 'words': [{'word': 'Hello?', 'start': 1.764, 'end': 2.084}]}, {'role': 'agent', 'content': "Hi there! This is Kate calling on behalf of Somebody. I'm reaching out today regarding setting up a new patient appointment. Before we proceed, I wanted to check ", 'words': [{'word': 'Hi ', 'start': 4.513, 'end': 4.757}, {'word': 'there! ', 'start': 4.757, 'end': 5.233}, {'word': 'This ', 'start': 5.278916748046875, 'end': 5.453916748046875}, {'word': 'is ', 'start': 5.453916748046875, 'end': 5.604916748046875}, {'word': 'Kate ', 'start': 5.604916748046875, 'end': 5.847916748046875}, {'word': 'calling ', 'start': 5.847916748046875, 'end': 6.149916748046875}, {'word': 'on ', 'start': 6.149916748046875, 'end': 6.265916748046875}, {'word': 'behalf ', 'start': 6.265916748046875, 'end': 6.579916748046875}, {'word': 'of ', 'start': 6.579916748046875, 'end': 6.683916748046875}, {'word': 'Somebody. ', 'start': 6.683916748046875, 'end': 7.415916748046875}, {'word': "I'm ", 'start': 7.450583251953125, 'end': 7.694583251953125}, {'word': 'reaching ', 'start': 7.694583251953125, 'end': 8.019583251953126}, {'word': 'out ', 'start': 8.019583251953126, 'end': 8.204583251953125}, {'word': 'today ', 'start': 8.204583251953125, 'end': 8.669583251953124}, {'word': 'regarding ', 'start': 8.669583251953124, 'end': 9.319583251953125}, {'word': 'setting ', 'start': 9.319583251953125, 'end': 9.633583251953125}, {'word': 'up ', 'start': 9.633583251953125, 'end': 9.737583251953126}, {'word': 'a ', 'start': 9.737583251953126, 'end': 9.807583251953124}, {'word': 'new ', 'start': 9.807583251953124, 'end': 9.946583251953125}, {'word': 'patient ', 'start': 9.946583251953125, 'end': 10.283583251953125}, {'word': 'appointment. ', 'start': 10.283583251953125, 'end': 11.084583251953125}, {'word': 'Before ', 'start': 11.119333251953124, 'end': 11.525333251953125}, {'word': 'we ', 'start': 11.525333251953125, 'end': 11.676333251953125}, {'word': 'proceed, ', 'start': 11.676333251953125, 'end': 12.152333251953126}, {'word': 'I ', 'start': 12.152333251953126, 'end': 12.233333251953125}, {'word': 'wanted ', 'start': 12.233333251953125, 'end': 12.547333251953125}, {'word': 'to ', 'start': 12.547333251953125, 'end': 12.651333251953124}, {'word': 'check ', 'start': 12.651333251953124, 'end': 12.953333251953126}], 'metadata': {'response_id': 1}}, {'role': 'user', 'content': 'Oh, ', 'words': [{'word': 'Oh, ', 'start': 13.034001, 'end': 13.354}]}, {'role': 'agent', 'content': 'if your office ', 'words': [{'word': 'if ', 'start': 12.953333251953126, 'end': 13.069333251953125}, {'word': 'your ', 'start': 13.069333251953125, 'end': 13.267333251953126}, {'word': 'office ', 'start': 13.267333251953126, 'end': 13.673333251953125}], 'metadata': {'response_id': 1}}, {'role': 'user', 'content': "sorry. We're not taking any new appointments.", 'words': [{'word': 'sorry. ', 'start': 13.354, 'end': 13.674}, {'word': "We're ", 'start': 13.674, 'end': 13.834}, {'word': 'not ', 'start': 13.834, 'end': 13.914}, {'word': 'taking ', 'start': 13.914, 'end': 14.154001}, {'word': 'any ', 'start': 14.154001, 'end': 14.394}, {'word': 'new ', 'start': 14.394, 'end': 14.554}, {'word': 'appointments.', 'start': 14.554, 'end': 14.954001}]}, {'role': 'agent', 'content': "I understand. Thank you for letting me know that you're not taking new appointments at this time. Before I go, could you confirm if you accept Some Insurance? This would be helpful information for future reference.", 'words': [{'word': 'I ', 'start': 17.411, 'end': 17.585}, {'word': 'understand. ', 'start': 17.585, 'end': 18.41}, {'word': 'Thank ', 'start': 18.444583251953127, 'end': 18.722583251953125}, {'word': 'you ', 'start': 18.722583251953125, 'end': 18.850583251953125}, {'word': 'for ', 'start': 18.850583251953125, 'end': 19.001583251953125}, {'word': 'letting ', 'start': 19.001583251953125, 'end': 19.245583251953125}, {'word': 'me ', 'start': 19.245583251953125, 'end': 19.338583251953125}, {'word': 'know ', 'start': 19.338583251953125, 'end': 19.524583251953125}, {'word': 'that ', 'start': 19.524583251953125, 'end': 19.651583251953124}, {'word': "you're ", 'start': 19.651583251953124, 'end': 19.849583251953124}, {'word': 'not ', 'start': 19.849583251953124, 'end': 20.000583251953124}, {'word': 'taking ', 'start': 20.000583251953124, 'end': 20.359583251953126}, {'word': 'new ', 'start': 20.359583251953126, 'end': 20.510583251953125}, {'word': 'appointments ', 'start': 20.510583251953125, 'end': 21.068583251953125}, {'word': 'at ', 'start': 21.068583251953125, 'end': 21.219583251953125}, {'word': 'this ', 'start': 21.219583251953125, 'end': 21.439583251953124}, {'word': 'time. ', 'start': 21.439583251953124, 'end': 21.985583251953123}, {'word': 'Before ', 'start': 22.008458251953126, 'end': 22.391458251953125}, {'word': 'I ', 'start': 22.391458251953125, 'end': 22.507458251953125}, {'word': 'go, ', 'start': 22.507458251953125, 'end': 22.821458251953125}, {'word': 'could ', 'start': 22.821458251953125, 'end': 23.030458251953124}, {'word': 'you ', 'start': 23.030458251953124, 'end': 23.146458251953124}, {'word': 'confirm ', 'start': 23.146458251953124, 'end': 23.599458251953124}, {'word': 'if ', 'start': 23.599458251953124, 'end': 23.703458251953126}, {'word': 'you ', 'start': 23.703458251953126, 'end': 23.819458251953126}, {'word': 'accept ', 'start': 23.819458251953126, 'end': 24.191458251953126}, {'word': 'Some ', 'start': 24.191458251953126, 'end': 24.388458251953125}, {'word': 'Insurance? ', 'start': 24.388458251953125, 'end': 25.189458251953123}, {'word': 'This ', 'start': 25.212833251953125, 'end': 25.549833251953125}, {'word': 'would ', 'start': 25.549833251953125, 'end': 25.769833251953123}, {'word': 'be ', 'start': 25.769833251953123, 'end': 25.886833251953124}, {'word': 'helpful ', 'start': 25.886833251953124, 'end': 26.246833251953124}, {'word': 'information ', 'start': 26.246833251953124, 'end': 26.780833251953126}, {'word': 'for ', 'start': 26.780833251953126, 'end': 26.942833251953125}, {'word': 'future ', 'start': 26.942833251953125, 'end': 27.256833251953125}, {'word': 'reference.', 'start': 27.256833251953125, 'end': 27.929833251953124}], 'metadata': {'response_id': 2}}, {'role': 'user', 'content': "Uh, no. We don't.", 'words': [{'word': 'Uh, ', 'start': 29.364, 'end': 29.444000000000003}, {'word': 'no. ', 'start': 29.444000000000003, 'end': 29.764000000000003}, {'word': 'We ', 'start': 29.764000000000003, 'end': 29.844}, {'word': "don't.", 'start': 29.844, 'end': 30.084}]}, {'role': 'agent', 'content': "I appreciate you letting me know that you don't accept Some Insurance. Thank you for your time today. Have a great day.", 'words': [{'word': 'I ', 'start': 33.436, 'end': 33.563}, {'word': 'appreciate ', 'start': 33.563, 'end': 34.016}, {'word': 'you ', 'start': 34.016, 'end': 34.156}, {'word': 'letting ', 'start': 34.156, 'end': 34.399}, {'word': 'me ', 'start': 34.399, 'end': 34.504}, {'word': 'know ', 'start': 34.504, 'end': 34.724}, {'word': 'that ', 'start': 34.724, 'end': 34.875}, {'word': 'you ', 'start': 34.875, 'end': 34.991}, {'word': "don't ", 'start': 34.991, 'end': 35.177}, {'word': 'accept ', 'start': 35.177, 'end': 35.502}, {'word': 'Some ', 'start': 35.502, 'end': 35.676}, {'word': 'Insurance. ', 'start': 35.676, 'end': 36.512}, {'word': 'Thank ', 'start': 36.558375, 'end': 36.779375}, {'word': 'you ', 'start': 36.779375, 'end': 36.895375}, {'word': 'for ', 'start': 36.895375, 'end': 37.023375}, {'word': 'your ', 'start': 37.023375, 'end': 37.174375}, {'word': 'time ', 'start': 37.174375, 'end': 37.418375}, {'word': 'today. ', 'start': 37.418375, 'end': 37.952375}, {'word': 'Have ', 'start': 37.998, 'end': 38.173}, {'word': 'a ', 'start': 38.173, 'end': 38.231}, {'word': 'great ', 'start': 38.231, 'end': 38.463}, {'word': 'day.', 'start': 38.463, 'end': 38.974}], 'metadata': {'response_id': 4}}, {'role': 'tool_call_invocation', 'tool_call_id': '719d03f9257a33fd', 'name': 'end_call', 'arguments': '{"execution_message": "I appreciate you letting me know that you don\'t accept Some Insurance. Thank you for your time today. Have a great day."}'}],
#     'recording_url': 'https://dxc03zgurdly9.cloudfront.net/d760844de28af31cc262892a38626bdc387e709994625372a03d9f93ba33d09f/recording.wav', 
#     'public_log_url': 'https://dxc03zgurdly9.cloudfront.net/d760844de28af31cc262892a38626bdc387e709994625372a03d9f93ba33d09f/public.log', 
#     'disconnection_reason': 'agent_hangup', 
#     'latency': {
#       'llm': {'p50': 2009, 'p90': 2509.7999999999997, 'p95': 2572.4, 'p99': 2622.48, 'min': 1693, 'max': 2635, 'num': 3, 'values': [2009, 1693, 2635]}, 'e2e': {'p50': 2341.9990234375, 'p90': 3047.5998046874997, 'p95': 3135.79990234375, 'p99': 3206.35998046875, 'min': 2313, 'max': 3224, 'num': 3, 'values': [2313, 2341.9990234375, 3224]}, 
#       'tts': {'p50': 241, 'p90': 347.4, 'p95': 360.7, 'p99': 371.34000000000003, 'min': 240, 'max': 374, 'num': 3, 'values': [240, 241, 374]}
#     }, 
#     'call_cost': {
#       'total_duration_unit_price': 0.2416667, 
#       'product_costs': [
#         {
#           'product': 'retell_platform', 
#           'unit_price': 0, 
#           'cost': 0
#         }, 
#         {
#           'product': 'elevenlabs_tts', 
#           'unit_price': 0.1166667, 
#           'cost': 4.55
#         }, 
#         {
#           'product': 'claude_3_7_sonnet', 
#           'unit_price': 0.1, 
#           'cost': 3.9
#         }, 
#         {
#           'product': 'us_telephony', 
#           'unit_price': 0.025, 
#           'cost': 0.975
#         }
#       ], 
#       'combined_cost': 9.425, 
#       'total_duration_seconds': 39
#     }, 
#     'call_analysis': {
#       'call_summary': 'The user informed the agent that they are not taking any new appointments and also confirmed that they do not accept Some Insurance. The agent thanked the user for their time and ended the call.', 
#       'in_voicemail': False, 
#       'user_sentiment': 'Neutral', 
#       'call_successful': True, 
#       'custom_analysis_data': {
#         'accepts_insurance': False, 
#         'accepting_new_patients': False, 
#         'scheduled_appointment': '', 
#         'additional_information': '', 
#         'appointment_booked': False
#       }
#     }, 
#     'opt_out_sensitive_data_storage': False, 
#     'opt_in_signed_url': False, 
#     'from_number': '+14152376335', 
#     'to_number': '+19254514431', 
#     'direction': 'outbound', 
#     'telephony_identifier': {
#       'twilio_call_sid': 'CA3ab83fcf046082fd094984f72c7c9495'
#     }
#   }
# }

def receive_webhook(call_data):
  if call_data['event'] != 'call_analyzed':
    print("Not a call_analyzed event. Exiting.")
    return
  
  # analysis data
  call_analysis = call_data['call']['call_analysis']
  custom_data = call_analysis['custom_analysis_data']

  return custom_data