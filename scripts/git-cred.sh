#!/bin/sh
echo username=x-access-token
echo password=$(cat /root/.secrets/github_pat)
