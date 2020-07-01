# created by Vishal Dogra on 25-06-2020
# created for issue https://rivigolabs.atlassian.net/browse/ZTS-91118

from MultipleConsignmentBlockerModule import MultipleConsignmentsBlockerService
from MultipleConsignmentBlockerModule import defaultEnums


def display_options_and_get_input():
    print("[+]" + str('-' * 10) + "Please choose one of the following" + str('-' * 10) + "[+]")
    user_selection = input("1.\t\tBLOCK CN(s)\n2.\t\tUNBLOCK CN(s)\n3.\t\tFetch Blocked CNs\n4.\t\tExit\nInput: ")
    return user_selection


def execution_flow(action):
    cn_ids = input(
        'Enter comma separated cn ids (in case of a single CN no need to append a comma): '
    ).strip().split(',')
    print("Input received -> ", cn_ids)
    print('Select one of the following reasons id:')
    print('ID \t\t Reason')
    for reason in defaultEnums.REASONS_MAP.keys():
        print(reason + "\t\t  " + defaultEnums.REASONS_MAP.get(reason).value.get('reason'))
    reason = input('Your selection here(reason id): ').strip()
    reason = defaultEnums.REASONS_MAP.get(reason)
    resp = multipleConsignmentBlockerService.act(action, cn_ids, reason)
    return resp


print("[+]---------------------------------------------------------[+]")
token = input("Enter SSO token: ")

while True:
    try:
        multipleConsignmentBlockerService = MultipleConsignmentsBlockerService()
        multipleConsignmentBlockerService.token = token
        print(
            "All requests will be generated on the behalf of {}".format(
                multipleConsignmentBlockerService.check_token().get(
                    'email'
                )
            )
        )
        choice = display_options_and_get_input()
        if choice == '1':
            act = defaultEnums.Actions.BLOCK
            response = execution_flow(act)
            print("Length of response received: ", len(response))
            print("Blocked CN ids with statuses -> \n ", response)
        elif choice == '2':
            act = defaultEnums.Actions.UNBLOCK
            response = execution_flow(act)
            print("Length of response received: ", len(response))
            print("Unblocked CN ids with statuses -> \n ", response)
        elif choice == '3':
            from_date = input('Enter the fromDate in format (YYYY-MM-DD): ')
            to_date = input('Enter the toDate in format (YYYY-MM-DD): ')
            if len(from_date) != 10 or len(to_date) != 10:
                print('Wrong length dates entered, setting date values to default.')
            multipleConsignmentBlockerService.fromDate = from_date if from_date else '2020-06-24'
            multipleConsignmentBlockerService.toDate = to_date if to_date else '2020-06-25'
            response = multipleConsignmentBlockerService.fetch([97, 98, 135, 136])
            print("consignment_id\t\treason_id\t\tCnote\t\t\tClient\t\tReason")
            for element in response.get('response'):
                print(
                    "{}\t\t\t\t\t{}\t\t  {}\t\t{}\t\t{}".format(
                        element.get('consignmentId'),
                        element.get('reasonId'),
                        element.get('cnote'),
                        element.get('clientCode'),
                        element.get('reason')
                    ))
        elif choice == '4':
            print("exiting......")
            break
        else:
            print("exiting......")
            break
        ch = input(
            "\nDo you wish to continue the session further? ('Y' or 'Yes' to continue, any other key for exiting.): ")
        if ch.upper() != 'Y' or ch.upper() != 'YES':
            break
    except Exception as e:
        print(e)
