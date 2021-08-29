# Flaty

This small project aims to give the possibility to use Js to make a web server and also keep the power of python in js.
So it is based on Flask for the web server, PySide2 for the Js, Peewee for the database.

### Requirements

- PySide2==5.15.2
- Flask==2.0.1
- peewee==3.14.4


### How to setup project

* Create new main project file as `.py` and add this

`main.py` 
```python
from Flaty.flaty import Flaty

app = Flaty(__name__)
app.run()

```

* Setup now request route path before run it

```python
app.add_routes('route/route.js')

```

* for that you need to create new route.js in route folder

`route.js` 
```js
Routers.route({
	name: "index", route: "/", methods: ["GET"],
	onCall: (request) => {
		return "200 Ok"
	}
})
Routers.route({
	name: "calculate", route: "/calc", methods: ["GET"],
	onCall: (request) => {
		let r = JSON.parse(request)
		if(r.n1 !== undefined && r.n2 !== undefined) {
			return "%1 + %2 = %3"
						.arg(r.n1)
						.arg(r.n2)
						.arg(parseInt(r.n1) + parseInt(r.n2))
		}
		else {
			return "No calcul"
		}
	}
})

```

