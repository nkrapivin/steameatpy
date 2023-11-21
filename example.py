from steameat import steameat


def main():
    # these values are usually constant, stored by you:
    testappid = 480 # your app id here!
    testkey = bytes(( 0x00 )) # bytes go here!
    testdata = bytes(( 0x00 )) # bytes go here!
    # obtained from the game (an HTTPS request?):
    clientticket = bytes(( 0x00 )) # bytes go here!
    
    context = steameat.library_context()
    print(f'Library located in {context.get_library_path()}')
    decrypted_ticket = context.decrypt(clientticket, testkey)
    if not decrypted_ticket:
        print('Decryption failed!')
    else:
        print('Ticket decrypted, self testing...')

        if decrypted_ticket.app_id != testappid:
            print('App ID does not match the expected one!')
        
        if decrypted_ticket.user_data != testdata:
            print('User defined ticket data does not match the expected one!')
        
        print(f'Ticket App ID:                   {decrypted_ticket.app_id}')
        print(f'Ticket Steam ID:                 {decrypted_ticket.steam_id}')
        print(f'Issue time (UTC):                {decrypted_ticket.issue_time}')
        print(f'Is user VAC banned for this app? {decrypted_ticket.is_vac_banned}')
        print(f'Is license borrowed?             {decrypted_ticket.is_license_borrowed}')
        print(f'Is license temporary?            {decrypted_ticket.is_license_temporary}')
        print(f'App defined value (unused?):     {decrypted_ticket.app_defined_value}')
        print(f'User defined ticket data:        {decrypted_ticket.user_data}')
        print(f'App ID test:                     {decrypted_ticket.is_ticket_for_app(testappid)}')
        print(f'App ID ownership test:           {decrypted_ticket.user_owns_app_in_ticket(testappid)}')


if __name__ == '__main__':
    main()

