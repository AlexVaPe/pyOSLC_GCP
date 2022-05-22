# GCP Python OSLC Adapter

Python implementation of an OSLC Adapter for Google Cloud Platform

## How to run locally the adapter

1. Clone the repository
2. Create a Google Cloud account or use an existing one
3. Go to the API Console: https://console.developers.google.com/.
4. From the projects list, select a project or create a new one, and choose Credentials from the left panel.
5. Click Create credentials and then select API key -> it will generate a .json file that you need to store at the root of the project.
6. Then, you need to modify the PROJECT_ID variable of the code with the id of your GCP project.
7. Modify the "command" of the docker-compose.yml to execute flask run command without --cert and --key options. This will run a flask server over http on http://localhost:5001 url.
8. For running the adapter, you need to execute:

```bash
docker-compose up
```

Then, the server will be up and running and you will be able to make http post requests to the Action Endpoint in order to create/delete GCP resources. For this, you can use an API client as Insomnia (https://insomnia.rest).

However, the server will not be able to receive logs from GCP as it is running locally. In order to make it publicly accessible, it is needed to follow the process that will be explained on the next section.

## Action Endpoint

Endpoint URL: http://0.0.0.0:5001/service/action

Headers of the request:

- Content-Type: application/rdf+xml
- Accept: application/rdf+xml

### Example of a GCS Bucket creation

Body:

```xml
<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
	xmlns:ns1="http://open-services.net/ns/core#"
	xmlns:ns2="http://localhost:5001/GCP_OSLC/"
	xmlns:action="http://open-services.net/ns/actions#"
	xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"

>
	<rdf:Description>
		<rdf:type rdf:resource="http://localhost:5001/GCP_OSLC/CreateDirectoryAction"/>
		<ns2:directoryName>test-adapter</ns2:directoryName>
		<ns2:directoryStorageClass>STANDARD</ns2:directoryStorageClass>
		<ns2:directoryLocation>US</ns2:directoryLocation>
	</rdf:Description>
</rdf:RDF>
```

### Example of a GCE Instance creation

Body:

```xml
<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
	xmlns:ns1="http://open-services.net/ns/core#"
	xmlns:ns2="http://localhost:5001/GCP_OSLC/"
	xmlns:action="http://open-services.net/ns/actions#"
	xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
>
	<rdf:Description>
	<rdf:type rdf:resource="http://localhost:5001/GCP_OSLC/CreateInstanceAction"/>
		<ns2:instanceName>test-instance-oslc</ns2:instanceName>
		<ns2:instanceZone>us-central1-c</ns2:instanceZone>
	</rdf:Description>
</rdf:RDF>
```

## How to make the adapter publicly accessible

1. First, it is recommended to run a GCE Instance on GCP and note the external ip of the machine.
2. Then, you need to follow the instructions of the following link: https://www.splitbrain.org/blog/2017-08/10-homeassistant_duckdns_letsencrypt, in order to get a domain and generate certificates for that domain and store them on the machine.
3. After that, you need to set up a Cloud Logging sink pointing to a Google Pub/Sub topic. You can follow Google official website: https://cloud.google.com/logging/docs/export/configure_export_v2#console.
4. Then, you need to create a push subscription on Google Pub/Sub (https://cloud.google.com/pubsub/docs/push), pointing to the domain that you already created followed by the logs endpoint: "https://your_domain-duckdns.org:5001/service/logs"
5. Finally, you need to include to the "command" field of the docker-compose.yml file the --cert and --key options that were originally included: "flask run -h 0.0.0.0 --cert=/code/certs/cert.pem --key=/code/certs/privkey.pem"

Now, the interaction with the server is equal as before, but the url needs to be changed to the new one: "https:your_domain-duckdns.org:5001/service/action".

## Adding the Event Server

In order to add the Event Server, the following steps need to be done:

1. "oslc_events" branch need to be cloned on a different path.
2. On the "main" cloned branch directory, mofify "event_endpoint" variable on resourceOSLC.py file with "http:your_domain-duckdns.org:5002/service/event/payload" endpoint (yes, now it's http not https).
3. On "oslc_events" cloned branch root path, execute:

```bash
docker-compose up
```

Finally, you will have two flask servers running on different ports on the same machine. One will run over https and will be publicly accessible so you can post Actions resource to it. The other will run over http and will receive Events when performing actions over the main server.
