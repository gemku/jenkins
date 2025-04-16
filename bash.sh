#!/bin/bash
kubectl config --kubeconfig=kube_custom.config set-cluster development --server=http://0.0.1.1 --certificate-authority=temp_ca_file
kubectl config --kubeconfig=kube_custom.config set-cluster staging --server=http://5.6.7.8 --certificate-authority=temp_ca_file
kubectl config --kubeconfig=kube_custom.config set-context dev-frontend --cluster=development --namespace=frontend --user=developer
kubectl config --kubeconfig=kube_custom.config set-context dev-staging --cluster=staging --namespace=frontend --user=developer
echo "Contents of kube_custom.config:"
cat kube_custom.config

