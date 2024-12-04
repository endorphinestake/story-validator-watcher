import schedule
from parse.parse import Parse
from parse.get_subprocess_link import get_command
import subprocess

def main():
    tokens = Parse().run()
    if tokens:
        command = get_command(tokens)
        try:
            print('Run subprocess: ',' '.join(command))
            subprocess.run(command)
        except Exception as ex:
            print(ex)

if __name__ == '__main__':
    main()
    schedule.every(3).seconds.do(main)
    while True:
        schedule.run_pending()
    
