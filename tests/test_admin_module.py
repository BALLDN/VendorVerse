def test_handle_approvals_approve_user(test_client, mock_firestore):
    """
    A3-1 Approve Vendor Account Registration
    A4-1 Approve Employee Account Registration
    """
    mock_db, mock_doc_ref = mock_firestore
    mock_doc_ref.get.return_value.exists = True

    response = test_client.post(
        '/admin/', data={'action': 'approve', 'userIdField': 'test_user_id'})

    assert response.status_code == 302
    mock_doc_ref.update.assert_called_with({'Status': 'A'})


def test_handle_approvals_deny_user(test_client, mock_firestore):
    """
    A3-2 Deny Vendor Account Registration
    A4-2 Deny Employee Account Registration
    """
    mock_db, mock_doc_ref = mock_firestore
    mock_doc_ref.get.return_value.exists = True

    response = test_client.post(
        '/admin/', data={'action': 'deny', 'userIdField': 'test_user_id'})

    assert response.status_code == 302
    mock_doc_ref.update.assert_called_with({'Status': 'D'})


def test_handle_approvals_approve_booking(test_client, mock_firestore):
    """
    A5-1 Approve Vendor Booking
    """

    mock_db, mock_doc_ref = mock_firestore
    mock_doc_ref.get.return_value.exists = True

    response = test_client.post(
        '/admin/', data={'action': 'approve', 'bookingIdField': 'test_booking_id'})

    assert response.status_code == 302
    mock_doc_ref.update.assert_called_with({'Status': 'A'})


def test_handle_approvals_deny_booking(test_client, mock_firestore):
    """
    A5-2 Deny Vendor Booking
    """
    mock_db, mock_doc_ref = mock_firestore
    mock_doc_ref.get.return_value.exists = True

    response = test_client.post(
        '/admin/', data={'action': 'deny', 'bookingIdField': 'test_booking_id'})

    assert response.status_code == 302
    mock_doc_ref.update.assert_called_with({'Status': 'D'})


def test_handle_approvals_entity_not_found(test_client, mock_firestore):
    """
    Test that a request for a non-existing entity returns a not found message.
    """
    mock_db, mock_doc_ref = mock_firestore
    mock_doc_ref.get.return_value.exists = False

    response = test_client.post(
        '/admin/', data={'action': 'approve', 'bookingIdField': 'non_existing_booking_id'})

    assert response.status_code == 302  # Expecting a redirect
    with test_client.session_transaction() as sess:
        flashes = sess.get('_flashes', [])
        assert any(f[1] == 'Bookings not found' for f in flashes)


def test_handle_approvals_invalid_action(test_client, mock_firestore):
    """
    Test that a request with an invalid action returns an error.
    """
    mock_db, mock_doc_ref = mock_firestore
    mock_doc_ref.get.return_value.exists = True

    response = test_client.post(
        '/admin/', data={'action': 'invalid_action', 'bookingIdField': 'test_booking_id'})

    assert response.status_code == 302  # Expecting a redirect
    with test_client.session_transaction() as sess:
        flashes = sess.get('_flashes', [])
        assert any(f[1] == 'Invalid action' for f in flashes)
