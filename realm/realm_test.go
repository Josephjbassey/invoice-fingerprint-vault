package vault

import (
	"testing"
)

func TestRegisterInvoice(t *testing.T) {
	r := NewRealm()
	fp := "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
	submitter := "g1jg8mtutu9khhfwc4nxmuhcpftf0pajdhfvsqf5"
	docName := "sample-invoice.pdf"

	ts, err := r.RegisterInvoice(fp, submitter, docName)
	if err != nil {
		t.Fatalf("unexpected error registering invoice: %v", err)
	}
	if ts <= 0 {
		t.Fatalf("expected positive timestamp, got %d", ts)
	}
	if r.Count() != 1 {
		t.Fatalf("expected count 1, got %d", r.Count())
	}

	entry, err := r.GetEntry(fp)
	if err != nil {
		t.Fatalf("unexpected error getting entry: %v", err)
	}
	if entry.Fingerprint != fp || entry.Submitter != submitter || entry.DocumentName != docName {
		t.Fatalf("entry mismatch: %+v", entry)
	}

	// Duplicate registration should fail
	_, err = r.RegisterInvoice(fp, submitter, docName)
	if err == nil {
		t.Fatalf("expected error on duplicate registration, got nil")
	}
}
