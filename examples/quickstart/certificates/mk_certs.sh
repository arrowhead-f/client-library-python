#!/bin/bash

cd "$(dirname "$0")" || exit
source "lib_certs.sh"

create_root_keystore \
  "crypto/master.p12" "arrowhead.eu"

create_cloud_keystore \
  "crypto/master.p12" "arrowhead.eu" \
  "crypto/cloud.p12" "quickstart.python.arrowhead.eu"

create_consumer_system_keystore() {
  local SYSTEM_NAME=$1
  local SYSTEM_SANS=$2

  create_system_keystore \
    "crypto/master.p12" "arrowhead.eu" \
    "crypto/cloud.p12" "quickstart.python.arrowhead.eu" \
    "crypto/${SYSTEM_NAME}.p12" "${SYSTEM_NAME}.quickstart.python.arrowhead.eu" \
    "${SYSTEM_SANS}"
}

create_consumer_system_keystore "authorization"            "ip:127.0.0.1"
create_consumer_system_keystore "orchestrator"             "ip:127.0.0.1"
create_consumer_system_keystore "service_registry"         "ip:127.0.0.1"
create_consumer_system_keystore "event_handler"            "ip:127.0.0.1"

create_consumer_system_keystore "quickstart-consumer"         "ip:127.0.0.1"
create_consumer_system_keystore "quickstart-provider"         "ip:127.0.0.1"

create_sysop_keystore \
  "crypto/master.p12" "arrowhead.eu" \
  "crypto/cloud.p12" "quickstart.python.arrowhead.eu" \
  "crypto/sysop.p12" "sysop.quickstart.python.arrowhead.eu"

create_truststore \
  "crypto/truststore.p12" \
  "crypto/cloud.crt" "quickstart.python.arrowhead.eu"
