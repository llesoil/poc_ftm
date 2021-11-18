// Copyright 2015 Canonical Ltd.
// Licensed under the AGPLv3, see LICENCE file for details.

// The feature package defines the names of the current feature flags.
package feature

// JES stands for Juju Environment Server and controls access
// to the apiserver endpoints, api client and CLI commands.
const JES = "jes"

// Storage is the name of the feature to enable storage commands
// and server-side functionality.
const Storage = "storage"

// LogErrorStack is a developer feature flag to have the LoggedErrorStack
// function in the utils package write out the error stack as defined by the
// errors package to the logger.  The ability to log the error stack is very
// useful in those error cases where you really don't expect there to be a
// failure.  This means that the developers with this flag set will see the
// stack trace in the log output, but normal deployments never will.
const LogErrorStack = "log-error-stack"

// DbLog is the the feature which has Juju's logs go to
// MongoDB instead of to all-machines.log using rsyslog.
const DbLog = "db-log"
