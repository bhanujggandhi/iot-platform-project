from services import service_req
def wf_name_1(par_1 , par_2):
	D = dict()
	foo_op = service_req("foo", [par_1,par_2])
	D["foo"] = foo_op
	foobar_op = service_req("foobar", [])
	D["foobar"] = foobar_op
	bar_op = service_req("bar", [par_1,D["foo"]["key2"]])
	D["bar"] = bar_op

if __name__ == '__main__':
	wf_name_1(12,'ayush')