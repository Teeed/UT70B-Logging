#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>

#define BAUDRATE B2400

// Serial reading code from http://tldp.org/HOWTO/Serial-Programming-HOWTO/x115.html "3.2. Non-Canonical Input Processing"
int main(int argc, char **argv) {
	int fd,c, res;
	struct termios oldtio,newtio;
	char buf[255];

	if(argc < 2) {
		printf("Program that reads data form UT70B over RS232\nUsage: %s [device]\n", argv[0]);

		return 1;
	}

	fd = open(argv[1], O_RDWR | O_NOCTTY ); 
	if (fd <0) {perror(argv[1]); return 1; }

	tcgetattr(fd,&oldtio); /* save current port settings */

	memset(&newtio, 0, sizeof(newtio));
	newtio.c_cflag = BAUDRATE | CRTSCTS | CS8 | CLOCAL | CREAD;
	newtio.c_iflag = IGNPAR;
	newtio.c_oflag = 0;

	newtio.c_lflag = 0;

	newtio.c_cc[VTIME]    = 0;
	newtio.c_cc[VMIN]     = 5;

	tcflush(fd, TCIFLUSH);
	tcsetattr(fd,TCSANOW,&newtio);


	int status;
	ioctl(fd, TIOCMGET, &status);
	status |= TIOCM_DTR;
	status &= ~TIOCM_RTS;
	ioctl(fd, TIOCMSET, &status);

	for(;;) {
		res = read(fd, buf, 100);

		int i = 0;

		for(; i<res; i++)
			putc(buf[i] & 0b01111111, stdout); // first byte is always wrong - remove it

		fflush(stdout);
	}

	tcsetattr(fd,TCSANOW,&oldtio);

	return 0;
}
