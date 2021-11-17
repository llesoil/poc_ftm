//go:generate stringer -type=FeatureFlag

package features

import (
	"fmt"
	"sync"
)

type FeatureFlag int

const (
	unused FeatureFlag = iota // unused is used for testing
	//   Deprecated features, these can be removed once stripped from production configs
	PerformValidationRPC
	ACME13KeyRollover
	SimplifiedVAHTTP
	TLSSNIRevalidation

	//   Currently in-use features
	AllowRenewalFirstRL
	// Check CAA and respect validationmethods parameter.
	CAAValidationMethods
	// Check CAA and respect accounturi parameter.
	CAAAccountURI
	// ProbeCTLogs enables HTTP probes to CT logs from the publisher
	ProbeCTLogs
	// HEAD requests to the WFE2 new-nonce endpoint should return HTTP StatusOK
	// instead of HTTP StatusNoContent.
	HeadNonceStatusOK
	// NewAuthorizationSchema enables usage of the new authorization storage schema
	NewAuthorizationSchema
	// RevokeAtRA enables revocation in the RA instead of ocsp-updater
	RevokeAtRA
	// SetIssuedNamesRenewalBit enables the SA setting the renewal bit for
	// issuedNames entries during AddCertificate.
	SetIssuedNamesRenewalBit
	// EarlyOrderRateLimit enables the RA applying certificate per name/per FQDN
	// set rate limits in NewOrder in addition to FinalizeOrder.
	EarlyOrderRateLimit
	// EnforceMultiVA causes the VA to block on remote VA PerformValidation
	// requests in order to make a valid/invalid decision with the results.
	EnforceMultiVA
	// MultiVAFullResults will cause the main VA to wait for all of the remote VA
	// results, not just the threshold required to make a decision.
	MultiVAFullResults
)

// List of features and their default value, protected by fMu
var features = map[FeatureFlag]bool{
	unused:                   false,
	AllowRenewalFirstRL:      false,
	TLSSNIRevalidation:       false,
	CAAValidationMethods:     false,
	CAAAccountURI:            false,
	ACME13KeyRollover:        false,
	ProbeCTLogs:              false,
	SimplifiedVAHTTP:         false,
	PerformValidationRPC:     false,
	HeadNonceStatusOK:        false,
	NewAuthorizationSchema:   false,
	RevokeAtRA:               false,
	SetIssuedNamesRenewalBit: false,
	EarlyOrderRateLimit:      false,
	EnforceMultiVA:           false,
	MultiVAFullResults:       false,
}

var fMu = new(sync.RWMutex)

var initial = map[FeatureFlag]bool{}

var nameToFeature = make(map[string]FeatureFlag, len(features))

func init() {
	for f, v := range features {
		nameToFeature[f.String()] = f
		initial[f] = v
	}
}

// Set accepts a list of features and whether they should
// be enabled or disabled, it will return a error if passed
// a feature name that it doesn't know
func Set(featureSet map[string]bool) error {
	fMu.Lock()
	defer fMu.Unlock()
	for n, v := range featureSet {
		f, present := nameToFeature[n]
		if !present {
			return fmt.Errorf("feature '%s' doesn't exist", n)
		}
		features[f] = v
	}
	return nil
}

// Enabled returns true if the feature is enabled or false
// if it isn't, it will panic if passed a feature that it
// doesn't know.
func Enabled(n FeatureFlag) bool {
	fMu.RLock()
	defer fMu.RUnlock()
	v, present := features[n]
	if !present {
		panic(fmt.Sprintf("feature '%s' doesn't exist", n.String()))
	}
	return v
}

// Reset resets the features to their initial state
func Reset() {
	fMu.Lock()
	defer fMu.Unlock()
	for k, v := range initial {
		features[k] = v
	}
}
