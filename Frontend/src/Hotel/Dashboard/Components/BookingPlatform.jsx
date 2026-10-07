import React from "react";
import DonutChart from "./DonutChart";

/**
 * Booking by platform — and why it is empty.
 *
 * This card used to draw six hardcoded shares (Direct Booking 61%, Booking.com
 * 12%, Agoda 11%, …) under a small "Sample" tag. Nothing in the API can produce
 * them: a reservation carries no channel, no booking source, and no report
 * aggregates one, so the figures could never have described this property. A
 * number on a dashboard reads as a measurement, and a tag the size of a
 * footnote does not undo that — an operator would plan around 61% direct.
 *
 * So the card renders the empty state and says why, which is the honest
 * answer until a source exists. When a channel field does land on the
 * reservation, `data` is the only line that changes: DonutChart already
 * handles loading, error, empty and non-zero states.
 */
const BookingPlatform = () => (
  <DonutChart
    title="Booking by Platform"
    data={[]}
    valueFormatter={(v) => `${v}%`}
    emptyMessage="No booking-source data yet. Reservations do not record the channel they came from, so there is nothing to break down by platform."
  />
);

export default BookingPlatform;
