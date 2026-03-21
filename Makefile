updateall:
	python3 odoo-bin -c odoo.conf -u all
dev:
	python3 odoo-bin -c odoo.conf --dev=all
run:
	python3 odoo-bin -c odoo.conf