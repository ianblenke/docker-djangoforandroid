all:
	docker build -t ianblenke/djangoforandroid .
	docker run -ti --rm -v $(PWD)/outputs/:/outputs djangoforandroid
