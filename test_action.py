from main import execute_action


# test_new_action = execute_action(
#     "CREATE_ACTION",
#     "Crea una action che faccia una chiamata API a https://jsonplaceholder.typicode.com/posts/1 e restituisca il titolo del post.",
# )

test_new_action = execute_action("LIST_ACTIONS_FILE", None)

print("RISULTATO ESECUZIONE ACTION:")
print(test_new_action)
