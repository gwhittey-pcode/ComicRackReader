.PHONY: po mo

po:
	xgettext -Lpython --output=messages.pot program.py libs/uix/kv/basescreen.kv libs/uix/kv/licence.kv libs/uix/kv/navdrawer.kv libs/utils/showplugins.py
	msgmerge --update --no-fuzzy-matching --backup=off data/locales/po/ru.po messages.pot
	msgmerge --update --no-fuzzy-matching --backup=off data/locales/po/en.po messages.pot

mo:
	mkdir -p data/locales/ru/LC_MESSAGES
	mkdir -p data/locales/en/LC_MESSAGES
	msgfmt -c -o data/locales/ru/LC_MESSAGES/ComicRackReader.mo data/locales/po/ru.po
	msgfmt -c -o data/locales/en/LC_MESSAGES/ComicRackReader.mo data/locales/po/en.po
