package vault

import (
	"errors"
	"time"
)

// InvoiceEntry records a single fingerprint registration.
type InvoiceEntry struct {
	Fingerprint  string `json:"fingerprint"`
	Submitter    string `json:"submitter"`
	Timestamp    int64  `json:"timestamp"`
	DocumentName string `json:"document_name"`
}

// Realm is the Go struct representation of the invoice fingerprint realm.
type Realm struct {
	entries     map[string]InvoiceEntry
	bySubmitter map[string][]string
	count       int64
}

// NewRealm creates a new empty vault realm.
func NewRealm() *Realm {
	return &Realm{
		entries:     make(map[string]InvoiceEntry),
		bySubmitter: make(map[string][]string),
		count:       0,
	}
}

// RegisterInvoice stores a new fingerprint on the realm.
func (r *Realm) RegisterInvoice(fingerprint, submitter, docName string) (int64, error) {
	if len(fingerprint) != 64 || !isHex(fingerprint) {
		return 0, errors.New("fingerprint must be 64 hex characters")
	}
	if submitter == "" {
		return 0, errors.New("submitter address is required")
	}
	if _, exists := r.entries[fingerprint]; exists {
		return 0, errors.New("fingerprint already registered")
	}

	ts := time.Now().Unix()
	entry := InvoiceEntry{
		Fingerprint:  fingerprint,
		Submitter:    submitter,
		Timestamp:    ts,
		DocumentName: docName,
	}

	r.entries[fingerprint] = entry
	r.bySubmitter[submitter] = append(r.bySubmitter[submitter], fingerprint)
	r.count++

	return ts, nil
}

// GetEntry returns the InvoiceEntry for a given fingerprint.
func (r *Realm) GetEntry(fingerprint string) (InvoiceEntry, error) {
	if len(fingerprint) != 64 || !isHex(fingerprint) {
		return InvoiceEntry{}, errors.New("invalid fingerprint format")
	}
	entry, ok := r.entries[fingerprint]
	if !ok {
		return InvoiceEntry{}, errors.New("fingerprint not registered")
	}
	return entry, nil
}

// GetEntriesBySubmitter returns all fingerprints registered by a given submitter.
func (r *Realm) GetEntriesBySubmitter(submitter string) ([]InvoiceEntry, error) {
	if submitter == "" {
		return nil, errors.New("submitter address is required")
	}
	fps, ok := r.bySubmitter[submitter]
	if !ok {
		return []InvoiceEntry{}, nil
	}
	entries := make([]InvoiceEntry, 0, len(fps))
	for _, fp := range fps {
		if entry, ok := r.entries[fp]; ok {
			entries = append(entries, entry)
		}
	}
	return entries, nil
}

// Count returns the total number of registered fingerprints.
func (r *Realm) Count() int64 {
	return r.count
}

func isHex(s string) bool {
	for i := 0; i < len(s); i++ {
		c := s[i]
		if !((c >= '0' && c <= '9') ||
			(c >= 'a' && c <= 'f') ||
			(c >= 'A' && c <= 'F')) {
			return false
		}
	}
	return true
}
