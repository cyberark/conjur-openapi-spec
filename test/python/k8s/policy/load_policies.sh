#!/usr/bin/env bash

set -eou pipefail

conjur login -i admin -p $CONJUR_ADMIN_PASSWORD

readonly POLICY_DIR="/policy"

# NOTE: generated files are prefixed with the test app namespace to allow for parallel CI
readonly POLICY_FILES=(
  "$POLICY_DIR/generated/$TEST_APP_NAMESPACE_NAME.project-authn.yml"
  "$POLICY_DIR/generated/$TEST_APP_NAMESPACE_NAME.cluster-authn-svc.yml"
  "$POLICY_DIR/generated/$TEST_APP_NAMESPACE_NAME.app-identity.yml"
)

for policy_file in "${POLICY_FILES[@]}"; do
  echo "Loading policy $policy_file..."
  conjur policy load -b root -f $policy_file
done

conjur logout
