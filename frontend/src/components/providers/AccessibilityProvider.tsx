"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';

export type Language = 'mr' | 'hi' | 'en';
export type FontSize = 'normal' | 'large';
export type AudienceRole = 'PILGRIM' | 'VOLUNTEER' | 'MEDICAL' | 'POLICE' | 'NGO' | 'TEMPLE' | 'GOVERNMENT';

interface AccessibilityContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  fontSize: FontSize;
  setFontSize: (size: FontSize) => void;
  audienceRole: AudienceRole;
  setAudienceRole: (role: AudienceRole) => void;
  t: (mr: string, en: string, hi?: string) => string;
}

const AccessibilityContext = createContext<AccessibilityContextType>({
  language: 'mr',
  setLanguage: () => {},
  fontSize: 'normal',
  setFontSize: () => {},
  audienceRole: 'PILGRIM',
  setAudienceRole: () => {},
  t: (mr, en) => mr,
});

export const AccessibilityProvider = ({ children }: { children: React.ReactNode }) => {
  const [language, setLanguageState] = useState<Language>('mr');
  const [fontSize, setFontSizeState] = useState<FontSize>('normal');
  const [audienceRole, setAudienceRoleState] = useState<AudienceRole>('PILGRIM');

  useEffect(() => {
    const savedLang = localStorage.getItem('warimitra_lang') as Language;
    if (savedLang) setLanguageState(savedLang);

    const savedSize = localStorage.getItem('warimitra_fontsize') as FontSize;
    if (savedSize) setFontSizeState(savedSize);

    const savedUser = localStorage.getItem('warimitra_user');
    if (savedUser) {
      try {
        const u = JSON.parse(savedUser);
        const r = (u.role || '').toUpperCase();
        if (r.includes('GOV') || r.includes('SUPER') || r === 'ADMIN') setAudienceRoleState('GOVERNMENT');
        else if (r.includes('MED')) setAudienceRoleState('MEDICAL');
        else if (r.includes('POLICE')) setAudienceRoleState('POLICE');
        else if (r.includes('NGO')) setAudienceRoleState('NGO');
        else if (r.includes('TEMPLE')) setAudienceRoleState('TEMPLE');
        else if (r.includes('VOLUNTEER')) setAudienceRoleState('VOLUNTEER');
        else setAudienceRoleState('PILGRIM');
      } catch (e) {}
    }
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('warimitra_lang', lang);
  };

  const setFontSize = (size: FontSize) => {
    setFontSizeState(size);
    localStorage.setItem('warimitra_fontsize', size);
  };

  const setAudienceRole = (role: AudienceRole) => {
    setAudienceRoleState(role);
    const savedUser = localStorage.getItem('warimitra_user');
    const u = savedUser ? JSON.parse(savedUser) : {};
    u.role = role;
    localStorage.setItem('warimitra_user', JSON.stringify(u));
  };

  const t = (mr: string, en: string, hi?: string) => {
    if (language === 'mr') return mr;
    if (language === 'hi') return hi || mr;
    return en;
  };

  return (
    <AccessibilityContext.Provider
      value={{
        language,
        setLanguage,
        fontSize,
        setFontSize,
        audienceRole,
        setAudienceRole,
        t,
      }}
    >
      <div className={fontSize === 'large' ? 'accessibility-large' : ''}>
        {children}
      </div>
    </AccessibilityContext.Provider>
  );
};

export const useAccessibility = () => useContext(AccessibilityContext);
