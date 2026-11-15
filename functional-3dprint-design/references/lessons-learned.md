# Lessons learned

Failures from real builds. Read this at the start of every project and check the model against
it before exporting. Add new entries as you go.

## 1. Confirm what a measurement means

**What happened:** On the PitVista display enclosure, mounting-hole spacing was measured
**outer edge to outer edge** of the holes, but the model used it as **centre-to-centre**.
The pegs landed one hole diameter apart from where they should have been.

**Rule:** Every spacing measurement gets an explicit definition in the measurement list
and in `MEASUREMENTS`. Convert in code (`centre = outer - hole_d`) so the conversion is visible.
Ask for a photo with the caliper in place when in doubt.

## 2. Threaded inserts change the hole a peg locates in

**What happened:** Locating pegs were sized for the board's mounting holes. Once heat-set
threaded inserts went into the mating holes, the inserts' bore was smaller than the original
hole, so the pegs no longer fit.

**Rule:** If a hole will receive a threaded insert, size any peg that goes into it to the
**insert's inner bore** (minus clearance). Make the peg thinner, and say so in the parameter name
(`peg_d_into_insert`).

## 3. Measure the real screen, not the datasheet

**What happened:** Clip posts were sized from the display's datasheet thickness. The actual
panel, with the flex cable and backlight bulge, was thicker, and the clips wouldn't close.

**Rule:** Measure panel thickness at the **thickest point** on the real part, and add
0.2–0.3 mm clearance. Leave room behind displays for flex cables.

## 4. Fit-test before the big print

**Rule:** Every interface gets a small fit-test piece printed with the final settings. It costs
minutes, and a failed full enclosure at 0.12 mm layers costs most of a day.

## 5. Mask before you paint

**Rule:** Primer and paint add about 0.05–0.15 mm per surface. Anything that slides or snaps must be
masked, or the clearance must be increased and fit-tested **after** finishing a test piece.
