from main import execute_action

# from actions.create_action import llm_create_action

# # Definiamo l'input utente
# user_input = "Creami una action che racconti barzellette divertenti."

# # Eseguiamo la funzione e stampiamo il risultato
# result = llm_create_action(user_input)
# print("RISULTATO CREAZIONE ACTION:")
# print(result)

# Eseguiamo la funzione e stampiamo il risultato
# result = execute_action("GET_ACTION", "Dammi la lista delle azioni disponibili.")

# print("RISULTATO IDENTIFICAZIONE ACTION:")
# print(result)

# Eseguiamo la funzione e stampiamo il risultato
test_new_action = execute_action(
    "GET_ACTION", "dammi la lista delle azioni disponibili."
)

print("RISULTATO ESECUZIONE ACTION:")
print(test_new_action)
