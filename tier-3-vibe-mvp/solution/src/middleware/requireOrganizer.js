function requireOrganizer(req, res, next) {
  if (req.session && req.session.organizer) {
    return next();
  }
  return res.status(401).json({ error: 'Organizer login required.' });
}

module.exports = requireOrganizer;
