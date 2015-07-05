SED = sed
INCLUDE_DIR = /usr/include/

systemd/id128-constants.h: $(INCLUDE_DIR)/systemd/sd-messages.h
	$(SED) -n -r 's/,//g; s/#define (SD_MESSAGE_[A-Z0-9_]+)\s.*/add_id(m, "\1", \1) JOINER/p' <$< >$@
